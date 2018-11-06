#!/usr/bin/env groovy

pipeline {
  agent none
  environment {
    WEB_PAGE_TEST = credentials('WEB_PAGE_TEST')
    WEBPAGETEST_SERVER = "https://${WEB_PAGE_TEST}@wpt-api.stage.mozaws.net/"
  }
  options {
    timestamps()
    timeout(time: 15, unit: 'MINUTES')
  }
  stages {
    stage('clone') {
       agent any
       steps {
         checkout([
           $class: 'GitSCM',
           branches: [[name: 'master']],
           extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'webpagetest-api']],
           userRemoteConfigs: [[url: 'https://github.com/marcelduran/webpagetest-api']]])
        }
    }
    stage('Run webpagetest') {
      agent {
        dockerfile { dir 'webpagetest-api' }
      }
      steps {
        writeFile([
          file: 'commands.txt',
          text: """test ${URL} --location us-east-1-linux:Firefox --bodies --keepua -r 3 --first --poll --reporter json --label ${NAME}.fx.release
test ${URL} --location us-east-1-linux:Firefox Nightly --bodies --keepua -r 3 --first --poll --reporter json --label ${NAME}.fx.nightly
test ${URL} --location us-east-1-linux:Chrome --bodies --keepua -r 3 --first --poll --reporter json --label ${NAME}.chrome.release
test ${URL} --location us-east-1-linux:Chrome Canary --bodies --keepua -r 3 --first --poll --reporter json --label ${NAME}.chrome.canary"""])
        sh '/usr/src/app/bin/webpagetest batch commands.txt > "wpt.json"'
      }
      post {
        always {
          archiveArtifacts 'commands.txt,wpt.json'
        }
        success {
          stash includes: 'wpt.json', name: 'wpt.json'
        }
      }
    }
    stage('Submit stats to datadog') {
      agent {
        dockerfile {
          args '--net host'
        }
      }
      steps {
        unstash 'wpt.json'
        sh 'python ./send_to_datadog.py'
      }
    }
  }
}
