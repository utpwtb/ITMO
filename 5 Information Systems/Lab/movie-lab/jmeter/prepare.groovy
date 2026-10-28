import groovy.json.*
import java.util.concurrent.*
def fixture = new JsonSlurper().parse(new File(props.getProperty('fixtureFile')))
def round = Integer.parseInt(vars.get('iteration'))
def action = fixture.rounds[round].actions[ctx.getThreadNum()]
vars.put('iteration',(round+1).toString())
vars.putObject('action',action)
vars.put('targetPath',action.path)
vars.put('targetMethod',action.method)
vars.put('targetBody',action.body == null ? '' : JsonOutput.toJson(action.body))
vars.put('uploadFile',action.file ?: '')
vars.put('isUpload',(action.file != null).toString())
vars.put('isCrud',(action.file == null).toString())
vars.put('hasRead',(action.read != null).toString())
vars.put('readPath',action.read ?: '/')
vars.put('round',round.toString())
synchronized(props) {
    def key='barrier.'+round
    if(!props.containsKey(key)) props.put(key,new CyclicBarrier(Integer.parseInt(props.getProperty('threads','2'))))
}
SampleResult.setResponseCode('200')
SampleResult.setSuccessful(true)
