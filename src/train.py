# don t print wanrning in console
import warnings
warnings.filterwarnings('ignore')

import os
import shutil
import json
import sys
import yaml
from pathlib import Path
import logging
import argparse


import tensorflow as tf
print(tf.__version__)
from tensorflow.keras.applications import VGG16
import pandas as pd
import mlflow
import mlflow.keras
import mlflow.tensorflow


from utils.params_fct import params_fct
from utils.train.arch_model import Arch_model
from utils.generator import generator
from utils.utils_functions import delete_spaces

def main ():
    # create logger
    logging.basicConfig(stream= sys.stdout, level= logging.INFO)
    logger=logging.getLogger()
    logger.info("> start train script")


    parser= argparse.ArgumentParser(description="evaluate trained model")
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
        "model_artifact_path",
        metavar="model_artifact_path",
        type=str,
        help="the path for for stock model artifact")

    parser.add_argument(
        "history_df_path",
        metavar="history_df_path",
        type=str,
        help=" the path of for stock training history file",
    )

    parser.add_argument(
        "run_info_path",
        metavar="run_info_path",
        type=str,
        help="the path for stock run_info.json",
    )
    args =parser.parse_args()
    
    train_data_path = delete_spaces(args.train_data_path) #  traing data path
    validation_data_path = delete_spaces (args.validation_data_path) #  validation data path
    output_model_path = delete_spaces ( args.model_artifact_path) # model artifact folder path: where we stock the model 
    output_history_path= delete_spaces( args.history_df_path) # history folder path : where we stock this file
    run_info_path=  delete_spaces( args.run_info_path) #  the path where to save run_info.json :

    logger.info("> print args of train.py")
    logger.info("train_path: '{}'".format( train_data_path ))
    logger.info( "validation_path '{}'".format( validation_data_path))
    logger.info( "model_artifact_path: '{}'".format( output_model_path))
    logger.info( "history_path: '{}'".format( output_history_path))
    logger.info( "run_info_path:'{}'".format( run_info_path))   



    # load params
    logger.info("> load params")

    params =params_fct()
    with open("params.yaml" , "r" ) as params_file:
        params_dict= yaml.safe_load(params_file)["train"]
    logger.info(repr(params))
    logger.info(repr(params_dict))




    # create results/training folder to stock training artifact
    Path(output_model_path).mkdir(parents=True,exist_ok=True)
    Path(output_history_path).mkdir(parents=True,exist_ok=True)

    generatorobjet=generator(rescale=params.rescale,
                            image_size=params.image_size,
                            batch_size=params.batch_size,
                            train_path=train_data_path,
                            validation_path= validation_data_path
                            )


    base_model_1 = VGG16(include_top =params.include_top,
                        input_shape =params.input_shape)
    arch_model=Arch_model(base_model= base_model_1,class_number=generatorobjet.class_number)
    model_=arch_model.model
    model_.compile(optimizer=params.optimizer, loss=params.loss, metrics= params.metrics )

    logger.info("> try connect mlflow server" )

    mlflow_server_url= params_dict["mlflow_server_url"]
    experiment_name=  params_dict["experiment_name"] 
    mlflow.set_tracking_uri( mlflow_server_url)
    mlflow.set_experiment(experiment_name)

    if mlflow.get_tracking_uri()== mlflow_server_url:
        logger.info("> successful connect mlflow server "+mlflow_server_url )
    else:
        logger.error("can't connect mlflow server" )

    with mlflow.start_run() as run:
        logger.info("> start training the model")

        history=model_.fit(generatorobjet.train_generator,
                    epochs= params.nbr_epoch,
                    validation_data=generatorobjet.validation_generator)
        logger.info("> finish training the model")

        history_df = pd.DataFrame(history.history)
        history_path= os.path.join(output_history_path,"history.csv" )
        history_df.to_csv(history_path ,index=False)
        
        # remove  model_artifact folder to results ,else he give exception
        if Path(output_model_path).exists():  
            shutil.rmtree(output_model_path)
        mlflow.keras.save_model(model_, output_model_path)
        
        logger.info("run id: {}".format(run.info.run_id))
        logger.info("> start upload training artifact to mlflow serve".format(run.info.run_id))
        mlflow.log_params(params_dict)
        mlflow.log_artifact(history_path)
        mlflow.keras.log_model(model_,"keras")
        logger.info("> finish upload training artifact to mlflow serve".format(run.info.run_id))

    


    run_id= run.info.run_id
    experiment_id =run.info.experiment_id
    experiment_name= mlflow.get_experiment( experiment_id).name  
    run_info= {
        "experiment_id" : experiment_id,
        "experiment_name": experiment_name,
        "run_id": run_id,
        "mlflow_server_url": mlflow.get_tracking_uri(),
    }


    with open( os.path.join( run_info_path , "run_info.json"), "w" ) as run_info_file:
        run_info_file.write(json.dumps(run_info) )

if __name__ == "__main__":
    main()
 




