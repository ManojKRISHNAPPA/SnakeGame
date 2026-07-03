pipeline{
    agent any

    tools {
        maven 'maven'
        jdk 'java-17'
    }

    environment{
        IMAGE_NAME = "manojkrishnappa/snakegame:${GIT_COMMIT}"
        AWS_REGION = "ap-northeast-1"
        CLUSTER_NAME = "itkannadigaru-cluster"
        NAMESPACE = "microdegree"
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
                    clusterName: 'itkannadigaru-cluster',
                    contextName: '',
                    credentialsId: 'kube',
                    namespace: 'microdegree',
                    restrictKubeConfigAccess: false,
                    serverUrl: 'https://8930771D766366BE2F89B1F9126656A7.gr7.ap-northeast-1.eks.amazonaws.com'
                ) {
                    sh '''
                    sed -i "s|replace|${IMAGE_NAME}|g" deployment.yml
                    kubectl apply -f deployment.yml -n ${NAMESPACE}
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withKubeConfig(
                    caCertificate: '',
                    clusterName: 'itkannadigaru-cluster',
                    contextName: '',
                    credentialsId: 'kube',
                    namespace: 'microdegree',
                    restrictKubeConfigAccess: false,
                    serverUrl: 'https://8930771D766366BE2F89B1F9126656A7.gr7.ap-northeast-1.eks.amazonaws.com'
                ) {
                    sh '''
                    kubectl get pods -n ${NAMESPACE}
                    kubectl get svc -n ${NAMESPACE}
                    '''
                }
            }
        }
    }
}