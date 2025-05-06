# -*- coding: utf-8 -*-

"""
Main script for running the binary classification project pipeline.
"""

import argparse
import logging
from pathlib import Path
import sys
import time

from src.data import build_features

# Setup logging
logging.basicConfig(
    level  = logging.INFO, 
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(args):
    """
    Main function to run the entire pipeline or specific steps.
    """
    start_time = time.time()
    
    if args.all or args.data:
        logger.info('Making dataset...')
        data_instance = build_features.featureData(stage='remove')
        stage_1_data  = data_instance.get_features()
        stage_1_data.write_csv('data/features/stage_rm_features.csv')
    
    # if args.all or args.train:
    #     logger.info('Training models...')
    #     for model_type in ['logistic', 'svc', 'decision_tree', 'random_forest', 'xgboost']:
    #         if getattr(args, model_type, False):
    #             logger.info(f'Training {model_type} model...')
    #             train_model.run(model_type=model_type)
    #         elif args.all:
    #             logger.info(f'Training {model_type} model...')
    #             train_model.run(model_type=model_type)
    
    logger.info(f"Pipeline completed in {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Run the ML pipeline')
    parser.add_argument(
        '--all', 
        action = 'store_true', 
        help   = 'Run entire pipeline'
    )
    parser.add_argument(
        '--data', 
        action = 'store_true', 
        help   = 'Run data processing'
    )
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        args.all = True
    
    main(args)