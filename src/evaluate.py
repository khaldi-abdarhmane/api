from utils.Loadingmodel_data import modelLoad,historyLoad 
import sys
from utils.evaluate.observing_accuracy import observing_accuracy
from utils.evaluate.classification_report import classification_report_fct
from utils.generator import generator
from pathlib import Path
from utils.params_fct import params_fct
from utils.evaluate.confusion_matrix_plt import confusion_matrix_plt
import mlflow
import json
import os 

if len(sys.argv) != 10:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython train.py features model\n")
    sys.exit(1)

# create results/evaluate folder to stock evaluate artifact
Path("./../../results/evaluate/evaluate_plt/").mkdir(parents=True,exist_ok=True)
Path("./../../results/evaluate/evaluate_csv/").mkdir(parents=True,exist_ok=True)
artifact_path="./../../results"
    
#model_path = sys.argv[1]
model_artifact_path = sys.argv[1]
history_df_path = sys.argv[2]
validation_path = sys.argv[3]
output1 = sys.argv[4]

train_path = sys.argv[5]

output2 = sys.argv[6]
output3 = sys.argv[7]
observing_accuracy_path = sys.argv[8]
exploratory_artifact_path = sys.argv[9]


df=historyLoad(history_df_path)
model= mlflow.keras.load_model(model_artifact_path)
#model=modelLoad(model_path)
print("---- evaluate py load model from: [{}]".format(model_artifact_path) )

params=params_fct()

generatorobjet=generator(rescale=params.rescale,
                         image_size=params.image_size,
                         batch_size=params.batch_size,
                         train_path=train_path,
                         validation_path= validation_path
                        )

 
observing_accuracy(df=df,savepath= observing_accuracy_path)
classification_report_fct(validation_generator= generatorobjet.validation_generator,model=model,classification_report_path= output1,conf_matrix_path=output2)
confusion_matrix_plt(conf_matrix_path=output2,output=output3)



 

with open( os.path.join( artifact_path , "run_info.json"), "r" ) as run_info_file:
    run_info= json.load(run_info_file)


mlflow.set_tracking_uri( run_info['mlflow_server_url'])
mlflow.set_experiment( run_info["experiment_name"] )
print("---- get set_tracking_uri uri =",mlflow.get_tracking_uri())

 
with mlflow.start_run( run_id= run_info["run_id"] ) as last_run: 
    print("last_run run_id: {}".format(last_run.info.run_id))
    print("params: {}".format(last_run.data.params))
    print("status: {}".format(last_run.info.status))
    evaluation_artifact_path= "./../../results/evaluate/"
 

    mlflow.log_artifacts(evaluation_artifact_path)
    mlflow.log_artifacts(exploratory_artifact_path)




 
 

