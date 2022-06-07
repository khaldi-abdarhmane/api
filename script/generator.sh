#!/bin/bash

################################################################
##                                                             #
##  Generateur de image_docker_trinig                          #
##                                                             #
################################################################


## Variables ####################################################

DIR1="${HOME}""/dataremote:/dataremote"
DIR="${HOME}/generato"
cd ..
fileRepo="${PWD}/*"
filedvc="${PWD}/.dvc"
filegit="${PWD}/.git"


cd script


USER_SCRIPT=${USER}

## Functions ####################################################

help(){

echo "USAGE :

  ${0##*/} [-h] [--help]
  
  Options :

    -h, --help : aides

    -a0, --setup : setup dev machine , this will install [docker,dvc,awscli] and configure aws keys

    -a1, --dockerGroup : add user to Docker group

    -a2, --awscli : config aws cli

    -a3, --build : build trainig image

    -a4, --push : push trainig image to ecr
                                                           
    -a5, --pull : pull trainig image from ecr
   
    -a6, --pullData : pull dataset from s3

    -a7, --start : start trainig pipleine
    
"
}



parser_options(){

case $@ in	
	-h|--help)
	  help
	;;
  -a0|--setup)
	  setup
	;;

  -a1|--dockerGroup)
	  docker-Group
	;;
  -a2|--awscli)
	  awscli
	;;

  -a3|--build)
	  build_trinig_image
	;;

  -a4|--push)
	  push_trinig_img_to_ecr
	;;
  -a5|--pull)
	  pull_trainig_image_from_ecr
	;;
  -a6|--pullData)
	  pull_data
	;;
  -a7|--start)
	  go_to_environment_trinig
	;;        
	*)
        echo "option invalide, lancez -h ou --help"
esac
}


build_trinig_image(){
echo "begin building image"
mkdir /tmp/scripte_1 
cp -r ./../* /tmp/scripte_1
cd /tmp/scripte_1/
mkdir build_image
cp environment_setup/training_container/Dockerfile build_image/Dockerfile
cp environment_setup/training_container/workstation.sh build_image/workstation.sh
cp dependencies/plant_disease_pipeline/requirements.txt build_image/requirements.txt
cd build_image/
docker build -t training_imag .
cd ..
rm -r build_image/
rm /tmp/scripte_1
echo "END building image"
}

push_trinig_img_to_ecr(){
echo "BEGIN TO CONICTION TO ECR"  
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 698324562600.dkr.ecr.us-east-1.amazonaws.com
echo "BEGIN TO CONICTION TO ECR"
docker tag training_imag:latest 698324562600.dkr.ecr.us-east-1.amazonaws.com/training_imag:latest
docker push 698324562600.dkr.ecr.us-east-1.amazonaws.com/training_imag:latest
echo "l image est push"
echo "end"
}

pull_trainig_image_from_ecr(){
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 698324562600.dkr.ecr.us-east-1.amazonaws.com
docker pull 698324562600.dkr.ecr.us-east-1.amazonaws.com/training_imag:latest
}


go_to_environment_trinig(){

mkdir /tmp/env
echo "Install Postgres"
echo "
version: '3.9'
services:
  web:
    build: .
    volumes:
       - ${DIR1}
    environment:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_REGION: us-east-1
    command: bash -c '/pipeline/a.sh'
" > /tmp/env/docker-compose.yml

echo "
#!/bin/bash

ls -la /dataremote
ls -la /dataremote/data
ls -la /dataremote/data/small_dataset
ls -la /dataremote/data/small_dataset/val

cp -rf /dataremote/data .
ls -la
cd ml_pipelines/
cd plant_disease_pipeline/
dvc repro
ls -la
"> /tmp/env/a.sh

echo "
FROM training_imag
WORKDIR /pipeline
COPY . .

"> /tmp/env/dockerfile

cd /tmp/env
cp -r ${fileRepo} /tmp/env
cp -r ${filedvc} /tmp/env
cp -r ${filegit} /tmp/env
chmod +777 a.sh
docker compose build --no-cache
docker compose up
rm -r /tmp/env

}
###############################################################################################################
##########################################################################################################
pull_data(){
  
echo "pull data to local remote"
mkdir -p ~/dataremote
cd ..
dvc remote default storagekhaldi
dvc pull data
cp -fr data ~/dataremote

}
#########################################################################################################################
###################################################################################################################################

docker-Group()
{

groupadd -g 500000 dockremap && 
groupadd -g 501000 dockremap-user && 
useradd -u 500000 -g dockremap -s /bin/false dockremap && 
useradd -u 501000 -g dockremap-user -s /bin/false dockremap-user

echo "dockremap:500000:65536" >> /etc/subuid && 
echo "dockremap:500000:65536" >>/etc/subgid

echo "
  {
   \"userns-remap\": \"default\"
  }
" > /etc/docker/daemon.json

systemctl daemon-reload && systemctl restart docker


}

setup(){

echo "begin instalation tools"
echo "begin instalation docker"
apt-get update
apt-get install ca-certificates curl gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
echo "end instalation docker"

echo "[3]: install DVC "
wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list
wget -qO - https://dvc.org/deb/iterative.asc | sudo apt-key add -
apt update -qq -y
apt install -qq -y dvc
echo "END install DVC "

echo "[3]: install awscli "
apt update -qq -y
apt-get install -qq -y awscli
echo "end install awscli"




}


##################################################################################################################
awscli(){

aws configure

}
## Execute #####################################################################################

parser_options $@