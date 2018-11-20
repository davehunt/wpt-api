import groovy.json.JsonSlurper

def inputFile = new File('top50.json')
def targets = new JsonSlurper().parseText(inputFile.text)

folder('wpt-top50') {
  description('Folder for WebPageTest jobs')
}

for(target in targets) {
  pipelineJob("wpt-top50/${name.toLowerCase()}") {
    description("Run WebPageTest against ${target.name} (${target.url})")
    logRotator {
      daysToKeep(10)
      artifactDaysToKeep(10)
    }
    triggers {
      cron('H H/4 * * *')
    }
    environmentVariables {
      env('TARGET_URL', "${target.url}")
      env('TARGET_NAME', "${target.name.toLowerCase().replaceAll('[\\. ]', '-')}")
    }
    definition {
      cpsScm {
        scm {
          github('mozilla/wpt-api', 'job-dsl-top50')
        }
        scriptPath('Jenkinsfile')
      }
    }
  }
}
