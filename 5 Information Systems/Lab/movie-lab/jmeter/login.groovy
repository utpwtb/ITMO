import groovy.json.JsonSlurper
if(prev.getResponseCode() != '200') {prev.setSuccessful(false); throw new IllegalStateException('Login failed')}
def response = new JsonSlurper().parseText(prev.getResponseDataAsString())
assert response.csrf && response.authenticated
vars.put('csrf',response.csrf)
