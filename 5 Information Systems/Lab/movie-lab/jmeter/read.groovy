import groovy.json.JsonSlurper
def action = vars.getObject('action')
if(prev.getResponseCode() != '200') {prev.setSuccessful(false);throw new IllegalStateException('Target was not read before barrier')}
def object = new JsonSlurper().parseText(prev.getResponseDataAsString())
if(object.version != action.version) {prev.setSuccessful(false);throw new IllegalStateException('All participants must hold the same fixture version')}
