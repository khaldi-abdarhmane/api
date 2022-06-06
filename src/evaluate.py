# don t print wanrning in console
import warnings
warnings.filterwarnings('ignore')

import os 
import sys
from pathlib import Path
import json
import argparse
import logging

from utils.Loadingmodel_data import historyLoad 
from utils.evaluate.observing_accuracy import observing_accuracy
from utils.evaluate.classification_report import classification_report_fct
from utils.evaluate.confusion_matrix_plt import confusion_matrix_plt
from utils.generator import generator
from utils.params_fct import params_fct
from utils.utils_functions import delete_spaces
import mlflow


def main():
    parser= argparse.ArgumentParser(description="evaluate trained model")
    parser.add_argument(
        "model_artifact_path",
        metavar="model_artifact_path",
        type=str,
        help="the path for model artifact")

    parser.add_argument(
        "history_df_path",
        metavar="history_df_path",
        type=str,
        help=" the path of history.csv",
    )
    parser.add_argument(
        "train_data_path",
        metavar="train_data_path",
        type=str,
        help=" the path of training dataset",
    )
    parser.add_argument(
        "validation_data_path",
        metavar="validation_data_path",
        type=str,
        help=" the path of validation dataset",
    )

    parser.add_argument(
        "evaluation_csv_artifact_path",
        metavar="evaluation_csv_artifact_path",
        type=str,
        help=" the path for stock evaluation csv artifact",
    )
    parser.add_argument(
        "evaluation_plt_artifact_path",
        metavar="evaluation_plt_artifact_path",
        type=str,
        help=" the path for stock evaluation plot artifact",
    )
    parser.add_argument(
        "exploratory_artifact_path",
        metavar="exploratory_artifact_path",
        type=str,
        help="the path of exploratory artifacts",
    )
    parser.add_argument(
        "run_info_path",
        metavar="run_info_path",
        type=str,
        help="the path of run_info.json",
    )
    args =parser.parse_args()

    model_artifact_path = delete_spaces(args.model_artifact_path)
    history_df_path = delete_spaces(args.history_df_path) 
    train_path = delete_spaces(args.train_data_path)  
    validation_path = delete_spaces(args.validation_data_path)
    evaluation_csv_artifact_path = delete_spaces(args.evaluation_csv_artifact_path)
    evaluation_plt_artifact_path = delete_spaces(args.evaluation_plt_artifact_path)
    exploratory_artifact_path = delete_spaces(args.exploratory_artifact_path)
    run_info_path=  delete_spaces(args.run_info_path)



    logging.basicConfig(stream= sys.stdout, level= logging.INFO)
    logger= logging.getLogger()

    logger.info("> print args of evaluate.py")
    logger.info( "model_artifact_path: '{}'".format( model_artifact_path))
    logger.info("history_df_path: '{}'".format( history_df_path))
    logger.info("train_path: '{}'".format( train_path ))
    logger.info( "validation_path '{}'".format( validation_path))
    logger.info( "evaluation_csv_artifact_path: '{}'".format(evaluation_csv_artifact_path) )
    logger.info(  "evaluation_plt_artifact_path:'{}'".format( evaluation_plt_artifact_path))
    logger.info( "exploratory_artifact_path'{}'".format(exploratory_artifact_path))
    logger.info( "run_info_path:'{}'".format( run_info_path))

    Path(evaluation_csv_artifact_path  ).mkdir(parents=True,exist_ok=True)
    Path(evaluation_plt_artifact_path  ).mkdir(parents=True,exist_ok=True)
    
    logger.info("> start loading model and history from results folder" )
    history_df=historyLoad(history_df_path)
    model= mlflow.keras.load_model(model_artifact_path)
    logger.info("> Loading model and history finished" )

    params=params_fct()
    generatorobjet=generator(rescale=params.rescale,
                            image_size=params.image_size,
                            batch_size=params.batch_size,
                            train_path=train_path,
                            validation_path= validation_path
                            )

    
    classification_report =  os.path.join( evaluation_csv_artifact_path ,"classification_report.csv") 
    confusion_matrix_csv =  os.path.join( evaluation_csv_artifact_path ,"confusion_matrix.csv") 
    confusion_matrix_img =    os.path.join(evaluation_plt_artifact_path, "confusion_matrix_img.png") 
    observing_accuracy_img =   os.path.join(evaluation_plt_artifact_path,"observing_accuracy_img.png")  
    
    logger.info("> start generating evaluation artifacts" )
    observing_accuracy(df=history_df,savepath=observing_accuracy_img)
    classification_report_fct(validation_generator= generatorobjet.validation_generator,model=model,classification_report_path= classification_report,conf_matrix_path=confusion_matrix_csv)
    confusion_matrix_plt(conf_matrix_path=confusion_matrix_csv ,output=confusion_matrix_img )
    logger.info("> finished generating evaluation artifacts" )

    
    # load run info from  run_info.json
    with open( os.path.join( run_info_path ), "r" ) as run_info_file:
        run_info= json.load(run_info_file)

    logger.info("> try connect mlflow server" )
    mlflow.set_tracking_uri( run_info['mlflow_server_url'])
    mlflow.set_experiment( run_info["experiment_name"] )
 

    if mlflow.get_tracking_uri()== run_info["mlflow_server_url"]:
        logger.info("> successful connect mlflow server "+run_info["mlflow_server_url"] )
    else:
        logger.error("can't connect mlflow server" )
    
    logger.info("> start upload evaluation and exploratory artifact to mlflow server ")
    with mlflow.start_run( run_id= run_info["run_id"] ) as last_run:  
        logger.info("artifact will upload to the run that have id: {}".format(last_run.info.run_id))
        logger.info("status of run {}: {}".format(last_run.info.run_id, last_run.info.status))
        # upload results/evaluate folder to mlflow server
        evaluation_artifact_path= Path(evaluation_plt_artifact_path).parent
        mlflow.log_artifacts(evaluation_artifact_path)
        # upload results/exploratory folder to mlflow server
        mlflow.log_artifacts(exploratory_artifact_path)
    logger.info("> finished upload evaluation and exploratory artifact to mlflow server ")


if __name__ == "__main__":
    main()

 
 

