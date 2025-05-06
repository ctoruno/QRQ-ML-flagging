library(haven)
library(glue)
library(readr)
library(dplyr)
library(purrr)
library(stringr)

path2data <- glue('{Sys.getenv("HOME")}/OneDrive - World Justice Project/Data Analytics/8. Data/QRQ')
raw_files <- list.files(path2data, pattern = '_raw.dta$')
names(raw_files) <- str_extract(raw_files, '(?<=QRQ_).*(?=_raw\\.dta)')
clean_files <- list.files(path2data, pattern = '_clean.dta$')
names(clean_files) <- str_extract(clean_files, '(?<=QRQ_).*(?=_clean\\.dta)')

scores <- c(
  "f_1", "f_2", "f_3", "f_4", "f_6", "f_7", "f_8",
  "f_1_2", "f_1_3", "f_1_4", "f_1_5", "f_1_6", "f_1_7",
  "f_2_1", "f_2_2", "f_2_3", "f_2_4", 
  "f_3_1", "f_3_2", "f_3_3", "f_3_4", 
  "f_4_1", "f_4_2", "f_4_3", "f_4_4", "f_4_5", "f_4_6", "f_4_7", "f_4_8", 
  "f_6_1", "f_6_2", "f_6_3", "f_6_4", "f_6_5", 
  "f_7_1", "f_7_2", "f_7_3", "f_7_4", "f_7_5", "f_7_6", "f_7_7", 
  "f_8_1", "f_8_2", "f_8_3", "f_8_4", "f_8_5", "f_8_6", "f_8_7"
)

data <- imap(
  list('raw'   = raw_files,
       'clean' = clean_files),
  function(stage_files, stage){
    
    stage_data <- imap(
      stage_files,
      function(f, edition_year){

        print(f)

        df <- read_dta(
          glue('{path2data}/{f}')
        ) %>%
          select(
            question, year, longitudinal, id_alex, country,
            all_of(scores)
          ) %>%
          mutate(
            edition = as.double(edition_year),
            roli    = rowMeans(
              across(scores[1:7]), na.rm = TRUE
            ),
            year = if_else(
              edition > 2020,
              year,
              year+1
            ),
            unid = paste(edition, id_alex, sep = '_')
          ) %>%
          select(unid, edition, country, year, question, longitudinal, roli, all_of(scores))
      }
    ) %>%
      reduce(bind_rows)
    
    write_csv(stage_data, glue('../data/historic-data/qrq-{stage}.csv'))

  }
)
