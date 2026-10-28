import java.util.concurrent.TimeUnit
def barrier = props.get('barrier.'+vars.get('round'))
barrier.await(20,TimeUnit.SECONDS)
SampleResult.setResponseCode('200')
SampleResult.setSuccessful(true)
