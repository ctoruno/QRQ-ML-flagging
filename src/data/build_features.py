"""
Main script to build feature data
"""

import polars as pl

# When a new country is added, the flagging system is different. It is based more on rankings rather 
# than in over-time changes.
country_additions = {
    '2020': ['The Gambia', 'Kosovo'],
    '2021': [
        'Congo, Rep.', 'Cyprus', 'Haiti', 'Ireland', 'Latvia', 'Lithuania', 
        'Luxembourg', 'Malta', 'Paraguay', 'Slovak Republic', 'Sudan'
    ],
    '2022': ['Gabon'],
    '2023': ['Kuwait', 'Montenegro']
}

country_additions_df = pl.DataFrame({
    "edition": [year for year, countries in country_additions.items() for _ in countries],
    "country": [country for countries in country_additions.values() for country in countries]
}).with_columns(
    pl.col('edition').cast(pl.Int64())
)


# Name corrections are used to match the country names in the QRQ database with the country names 
# in the historic data. Country names in the historic data are preferred.
name_corrections = {
    "Bahamas"           : "The Bahamas",
    "Cote d'Ivoire"     : "Côte d'Ivoire",
    "Czech Republic"    : "Czechia",
    "Egypt"             : "Egypt, Arab Rep.",
    "Gambia"            : "The Gambia",
    "Iran"              : "Iran, Islamic Rep.",
    "Kyrgyzstan"        : "Kyrgyz Republic",
    "Macedonia, FYR"    : "North Macedonia",
    "Republic of Korea" : "Korea, Rep.",
    "Russia"            : "Russian Federation",
    "Turkey"            : "Türkiye",
    "Turkiye"           : "Türkiye",
    "Venezuela"         : "Venezuela, RB"
}


class featureData:
    
    def __init__(self, stage: int):
        
        if stage not in ['remove', 'on-off']:
            raise Exception('Stage must be a string equal to "remove" or "on-off"')
        else:
            self.stage = stage

        
    def load_historic_data(self):

        qrq_data = {
            x: (
                pl.read_csv(
                    f'data/historic-data/qrq-{x}.csv',
                    null_values = 'NA'
                )
                .with_columns(
                    pl.col('country').replace_strict(
                        name_corrections,
                        default = pl.col('country')
                    ).alias('country')
                )
            )
            for x in ['raw', 'clean']
        }
        
        roli_data = (
            pl.read_excel('data/historic-data/ROLI-data.xlsx')
            .unpivot(index = ['country', 'year', 'code', 'region'])
            .filter(pl.col('year').is_in(['2019', '2020', '2021', '2022', '2023', '2024']))
            .with_columns(
                pl.col('year').cast(pl.Int64())
            )
            .select(['country', 'year', 'variable', 'value'])
        )

        tps_data = (
            pl.read_excel('data/historic-data/TPS-rank-diffs.xlsx')
            .with_columns(
                pl.col('country').replace_strict(
                    name_corrections,
                    default = pl.col('country')
                ).alias('country')
            )
        )
        
        return {
            'qrq_data'  : qrq_data,
            'roli_data' : roli_data,
            'tps_data'  : tps_data
        }
    
    def get_labels(self):
        return "...."

    def get_features(self):
        return "...."
    
    def process_data(self):
        
        historic_data = self.load_historic_data()

        # Drop experts from recent addition countries
        qrq_data_raw_filtered = (
            historic_data['qrq_data']['raw']
            .join(
                country_additions_df,
                on = ['country', 'edition'],
                how = 'anti'
            )
        )

        # Creating Y-labels
        if self.stage == 'remove':

            y_var = (
                historic_data['qrq_data']['clean']
                .select(['country', 'edition', 'unid'])
                .with_columns(
                    (pl.col('unid').is_in(historic_data['qrq_data']['clean']['unid']).not_())
                    .cast(pl.Int8)
                    .alias('dropped')
                )
            )

        if self.stage == 'on-off':

            y_var = (
                historic_data['qrq_data']['clean']
                .select(['country', 'edition', 'unid'])
                .with_columns(
                    (pl.col('unid').is_in(historic_data['qrq_data']['clean']['unid']).not_())
                    .cast(pl.Int8)
                    .alias('dropped')
                )
            )





        qrq_data_raw_processed = (
            historic_data['qrq_data']['raw']
            
            # Drop experts from recent addition countries
            .join(
                country_additions_df,
                on = ['country', 'edition'],
                how = 'anti'
            )

            # Feature engineering
            .with_columns(
                (pl.col('unid').is_in(historic_data['qrq_data']['clean']['unid']).not_())
                .cast(pl.Int8)
                .alias('dropped'),
                
                pl.col('roli').mean().over('country', 'edition')
                .alias('avg_country_score'),

                pl.col('roli').std().over('country', 'edition')
                .alias('std_country_score'),

                pl.col('roli').sum().over('country', 'edition')
                .alias('sum_roli'),

                pl.col('roli').count().over('country', 'edition')
                .alias('count_roli'),

                pl.col('roli')
                .filter(pl.col('longitudinal') == 1)
                .mean()
                .over('country', 'edition')
                .alias('avg_country_longitudinal_score'),

                pl.len().over('country', 'edition')
                .alias('pool_size'),

                pl.len().over('country', 'edition', 'question')
                .alias('question_pool'),

                pl.col('longitudinal').sum().over('country', 'edition')
                .alias('longitudinal_pool_size'),

                (pl.col('edition') - pl.col('year') )
                .alias('distance2edition')
            )
            .with_columns(
                (pl.col('roli') - pl.col('avg_country_score'))
                .alias('distance2mean'),
                
                (pl.col('longitudinal') * (pl.col('longitudinal_pool_size') / pl.col('pool_size')))
                .alias('longitudinal_prop'),

                (
                    (
                        pl.col('avg_country_score') - (
                            (pl.col('sum_roli') - pl.col('roli')) / 
                            (pl.col('count_roli') - 1)
                        )
                    ) 
                )
                .alias('leave_one_out_score'),
            )
            .join(
                (
                    historic_data['roli_data']
                    .filter(pl.col('variable') == 'roli')
                    .select(['country', 'year', 'value'])
                    .with_columns(
                        (pl.col('year') + 1)
                    )
                    .rename({'value' : 'prev_year_avg_score'})
                ),
                left_on  = ['country', 'edition'],
                right_on = ['country', 'year'],
                how = 'left'
            )
            .join(
                (
                    historic_data['tps_data']
                    .select(['country', 'edition', 'rd_avg'])
                ),
                on  = ['country', 'edition'],
                how = 'left'
            )
            .with_columns(
                (pl.col('distance2mean') / pl.col('std_country_score'))
                .alias('distance2mean_nstd'),

                ((pl.col('avg_country_longitudinal_score') - pl.col('roli'))/(1+pl.col('distance2mean')))
                .alias('distance2long'),

                ((pl.col('prev_year_avg_score') - pl.col('roli'))/(1+pl.col('distance2mean')))
                .alias('distance2pyear'),

                ((pl.col('avg_country_longitudinal_score') - pl.col('roli')) * (pl.col('prev_year_avg_score') - pl.col('roli')))
                .fill_null(
                    (pl.col('prev_year_avg_score') - pl.col('roli')) ** 2
                )
                .alias('trend_measure')
            )
            .with_columns(
                (pl.col('distance2mean') * (pl.col('rd_avg') / 100))
                .alias('distance_rdw')
            )
        )

        features = (
            qrq_data_raw_processed
            .select([
                'country', 'edition', 'unid',
                'dropped', 'distance2mean', 'trend_measure', 'leave_one_out_score', 'distance_rdw',
                'question_pool', 'longitudinal_prop', 'distance2edition'
            ])
        )

        return features
                        







