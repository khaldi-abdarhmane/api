# don t print wanrning in console
import warnings
warnings.filterwarnings('ignore')

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
"""
if len(sys.argv) != 9:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython train.py features model\n")
    sys.exit(1)
"""

""""
    cmd: python ./../../src/evaluate.py ./../../results/training/keras ./../../results/training/history/history.csv ./../../data/small_dataset/val/
     ./../../results/evaluate/evaluate_csv/classification_report.csv ./../../data/small_dataset/train/ ./../../results/evaluate/evaluate_csv/confusion_matrix.csv 
     ./../../results/evaluate/evaluate_plt/confusion_matrix_img.png ./../../results/evaluate/evaluate_plt/observing_accuracy_img.png
      ./../../results/exploratory/exploratory_img/plots/
model_artifact_path = sys.argv[1]
history_df_path = sys.argv[2]
validation_path = sys.argv[3]
output1 = sys.argv[4] # ./../../results/evaluate/evaluate_csv/classification_report.csv

train_path = sys.argv[5]

output2 = sys.argv[6] ./../../results/evaluate/evaluate_csv/confusion_matrix.csv
output3 = sys.argv[7]  ./../../results/evaluate/evaluate_plt/confusion_matrix_img.png 
observing_accuracy_path = sys.argv[8] ./../../results/evaluate/evaluate_plt/observing_accuracy_img.png
exploratory_artifact_path = sys.argv[9]

output2 = sys.argv[6]
output3 = sys.argv[7]
evaluation_plt_artifact_path = sys.argv[8]
"""
# dvc cmd in yaml : 
#     cmd: python   ${src}/evaluate.py   ${res.tr.model}   ${res.tr.history}/history.csv   ${data}/train/   ${data}/val/ \
#         ${res.eval.csv}   ${res.eval.plots}   ${res.exp.plots} ${results}/run_info.json  
# delete extars space from sysargs

#### delete spacing from args ====
for i in range(len(sys.argv)):     
    sys.argv[i]= sys.argv[i].replace(" ","")

model_artifact_path = sys.argv[1]
history_df_path = sys.argv[2] 
train_path = sys.argv[3]  
validation_path = sys.argv[4]
evaluation_csv_artifact_path = sys.argv[5]
evaluation_plt_artifact_path = sys.argv[6]
exploratory_artifact_path = sys.argv[7]
run_info_path=  sys.argv[8]
#evaluation_artifact_path= "./../../results/evaluate/"

print("________________args ___________________")
print( "model_artifact_path: '{}'".format( model_artifact_path))
print("history_df_path: '{}'".format( history_df_path))
print("train_path: '{}'".format( train_path ))
print( "validation_path '{}'".format( validation_path))
print( " evaluation_csv_artifact_path: '{}'".format(evaluation_csv_artifact_path) )
print(  "evaluation_plt_artifact_path:'{}'".format( evaluation_plt_artifact_path))
print( "exploratory_artifact_path'{}'".format(exploratory_artifact_path))
print( "run_info_path:'{}'".format( run_info_path))

#evaluation_csv_artifact_path=evaluation_csv_artifact_path.replace(" ", "")
Path(evaluation_csv_artifact_path  ).mkdir(parents=True,exist_ok=True)
Path(evaluation_plt_artifact_path  ).mkdir(parents=True,exist_ok=True)
 
#artifact_path="./../../results"

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

 
classification_report =  os.path.join( evaluation_csv_artifact_path ,"classification_report.csv") # ./../../results/evaluate/evaluate_csv/classification_report.csv
confusion_matrix_csv =  os.path.join( evaluation_csv_artifact_path ,"confusion_matrix.csv") #"./../../results/evaluate/evaluate_csv/confusion_matrix.csv" # 
confusion_matrix_img =    os.path.join(evaluation_plt_artifact_path, "confusion_matrix_img.png") #"./../../results/evaluate/evaluate_plt/confusion_matrix_img.png" 
observing_accuracy_img =   os.path.join(evaluation_plt_artifact_path,"observing_accuracy_img.png")  # "./../../results/evaluate/evaluate_plt/observing_accuracy_img.png"
 
observing_accuracy(df=df,savepath=observing_accuracy_img)
classification_report_fct(validation_generator= generatorobjet.validation_generator,model=model,classification_report_path= classification_report,conf_matrix_path=confusion_matrix_csv)
confusion_matrix_plt(conf_matrix_path=confusion_matrix_csv ,output=confusion_matrix_img )

 
# artifact_path = run_info_path 

with open( os.path.join( run_info_path ), "r" ) as run_info_file:
    run_info= json.load(run_info_file)


mlflow.set_tracking_uri( run_info['mlflow_server_url'])
mlflow.set_experiment( run_info["experiment_name"] )
print("---- get set_tracking_uri uri =",mlflow.get_tracking_uri())

 
with mlflow.start_run( run_id= run_info["run_id"] ) as last_run:  
    print("last_run run_id: {}".format(last_run.info.run_id))
    print("params: {}".format(last_run.data.params))
    print("status: {}".format(last_run.info.status))
    evaluation_artifact_path= Path(evaluation_plt_artifact_path).parent
    mlflow.log_artifacts(evaluation_artifact_path)
    mlflow.log_artifacts(exploratory_artifact_path)



 
 

