import groovy.json.*

def users = new JsonSlurper().parse(
    new File(props.getProperty('credentialsFile', '.runtime/lab2-users.json'))
)
def scenario = props.getProperty('scenario', 'C02')

if (!(scenario in ['C01', 'C02', 'C03'])) {
    throw new IllegalArgumentException('Choose scenario C01, C02 or C03')
}

def index = ctx.getThreadNum()
def user = users[scenario == 'C01' ? 2 + index % 2 : index % users.size()]
vars.put('loginBody', JsonOutput.toJson(user))
vars.put('iteration', '0')

SampleResult.setResponseCode('200')
SampleResult.setSuccessful(true)
