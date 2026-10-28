import groovy.json.*
def users = new JsonSlurper().parse(new File(props.getProperty('credentialsFile','.runtime/lab2-users.json')))
def scenario = props.getProperty('scenario','C03')
def index = ctx.getThreadNum()
def user = users[(scenario in ['C01','C02','C02D']) ? 2 + index % 2 : index % users.size()]
vars.put('loginBody',JsonOutput.toJson(user))
vars.put('iteration','0')
SampleResult.setResponseCode('200')
SampleResult.setSuccessful(true)
