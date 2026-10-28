import groovy.json.*
import java.nio.file.*
def action=vars.getObject('action')
def data
try { data=new JsonSlurper().parseText(prev.getResponseDataAsString()) }
catch(Exception ignored) { data=[:] }
int status
try {status=Integer.parseInt(prev.getResponseCode())} catch(Exception ignored){status=0}
boolean valid=action.expected.contains(status)
if(status == 409 && action.code) valid = valid && data.code == action.code
if(action.atomicRead) valid = valid && data instanceof List && data.size() in [0,2]
prev.setSuccessful(valid)
if(!valid)prev.setResponseMessage('Unexpected status/body: '+status+' '+data.code)
def record=[scenario:props.getProperty('scenario'), round:Integer.parseInt(vars.get('round')),
    participant:ctx.getThreadNum(), method:action.method,path:action.path,status:status,
    code:data instanceof Map ? data.code : null,operationId:data instanceof Map ? data.operationId : null,
    elapsed:prev.getTime(),passed:valid]
synchronized(props) {
    Files.writeString(Path.of(props.getProperty('resultFile')),JsonOutput.toJson(record)+'\n',StandardOpenOption.CREATE,StandardOpenOption.APPEND)
}
