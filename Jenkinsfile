pipeline{
    agent any

    tools {
        maven 'maven'
        jdk 'java-17'
    }

    environment{
        IMAGE_NAME = "manojkrishnappa/snakegame:${GIT_COMMIT}"
    }

    stages{
        stage('compile'){
            steps{
                sh '''
                echo 'Compiling the code...'
                mvn compile
                '''
            }
        }

        stage('build'){
            steps{
                sh '''
                echo 'Building the code...'
                mvn clean install
                '''
            }
        }

        stage('docker build'){
            steps{
                sh '''
                printenv
                echo 'Building the docker image...'
                docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        stage('Docker Login'){
            steps{
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh '''
                    echo 'Logging into Docker Hub...'
                    echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                    '''
                }
            }
        }

        stage('docker push'){
            steps{
                sh '''
                echo 'Pushing the docker image to Docker Hub...'
                docker push ${IMAGE_NAME}
                '''
            }
        }
    }
}