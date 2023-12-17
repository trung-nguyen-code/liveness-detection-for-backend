def changesInFiltering = false;

pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'HOURS') 
    }

    stages {

        stage('Check if Filtering is updated') {
            steps {
                script {
                    def changeLogSets = currentBuild.changeSets;
                    for (int i = 0; i < changeLogSets.size(); i++) {
                        def entries = changeLogSets[i].items;
                        for (int j = 0; j < entries.length; j++) {
                            def entry = entries[j];
                            def files = new ArrayList(entry.affectedFiles);
                            for (int k = 0; k < files.size(); k++) {
                                def file = files[k];
                                def filePath = file.path.split("/");
                                if (filePath.length > 3) {
                                    if (filePath[0] == 'POC' && filePath[1] == 'Filtering' && filePath[2] == 'server') {
                                        changesInFiltering = true;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    if (changesInFiltering) {
                        sh "docker build -t ltservicesmek/filtering-demo ./POC/Filtering/server/"
                        withDockerRegistry([ credentialsId: "dockerhub-credentials", url: "" ]) {
                            sh "docker push ltservicesmek/filtering-demo"
                        }
                    }
                }
            }
        }
        stage("Deploy") {
            steps {
                script {
                    if (changesInFiltering) {
                        sh "kubectl --kubeconfig /kubeconfig/data-engineering rollout restart deployment filtering-demo -n airflow";
                    }
                }
            }
        }

    }
}
