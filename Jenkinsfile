pipeline {
    agent any

    tools{
        maven 'maven'
        jdk 'java-17'
    }
    environment{
        IMAGE_NAME = "manojkrishnappa/snakegame:${GIT_COMMIT}"
        AWS_REGION = "ap-northeast-1"
        CLUSTER_NAME = "shab-cluster"
    }

    stages{
        stage('checkout'){
            steps{
                git branch:'md-devsecops', url: 'https://github.com/ManojKRISHNAPPA/SnakeGame.git'
            }
        }

        stage('compile'){
            steps{
                sh '''
                    mvn clean compile
                '''
            }
        }

        stage('build stage'){
            steps{
                sh '''
                    mvn clean install
                '''
            }
        }

        stage('docker build'){
            steps{
                sh '''
                    docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-cred',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"
                }
            }
        }
        stage('uploading docker image to dockerhub'){
            steps{
                sh '''
                    docker push ${IMAGE_NAME}
                '''
            }
        }
        stage('Update kubeconfig') {
                steps {
                    sh '''
                    aws eks update-kubeconfig \
                    --region ${AWS_REGION} \
                    --name ${CLUSTER_NAME}
                    '''
                }
            }

        stage('Deploy to EKS') {
            steps {
                withKubeConfig(
                    caCertificate: '',
                    clusterName: 'shab-cluster',
                    contextName: '',
                    credentialsId: 'kube',
                    namespace: 'default',
                    restrictKubeConfigAccess: false,
                    serverUrl: 'https://7E50CA6BE0601965431953536C45A7F0.gr7.ap-northeast-1.eks.amazonaws.com'
                ) {
                    sh '''
                    sed -i "s|replace|${IMAGE_NAME}|g" deployment.yml
                    kubectl apply -f deployment.yml 
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withKubeConfig(
                    caCertificate: '',
                    clusterName: 'shab-cluster',
                    contextName: '',
                    credentialsId: 'kube',
                    namespace: 'default',
                    restrictKubeConfigAccess: false,
                    serverUrl: 'https://7E50CA6BE0601965431953536C45A7F0.gr7.ap-northeast-1.eks.amazonaws.com'
                ) {
                    sh '''
                    kubectl get pods 
                    kubectl get svc 
                    '''
                }
            }
        }
    
    }

}
