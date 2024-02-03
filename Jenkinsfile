node {
    String confUrl = 'https://vijaik.atlassian.net/wiki/rest/api/content/33141?expand=body.storage'
    String appName = 'RMI Replatform'
    stage('Get Services Info') {
        checkout scm
        withCredentials([usernamePassword(credentialsId: 'CONFLUENCE', usernameVariable: 'CONFLUENCE_USERNAME', passwordVariable: 'CONFLUENCE_APITOKEN')]) {
            bat '''
            //String serviceInfoCommand = """
                python -m pip install -r requirements.txt --user
                python service-getter.py -u ${confUrl} -a ${appName}
            '''
            // """
            // def output = sh(returnStdout: true, script: serviceInfoCommand)
            // print(output)
        }
    }
}