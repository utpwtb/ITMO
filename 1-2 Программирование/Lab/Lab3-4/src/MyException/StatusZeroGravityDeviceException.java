package MyException;

public class StatusZeroGravityDeviceException extends RuntimeException {
    public StatusZeroGravityDeviceException() {
    }

    public StatusZeroGravityDeviceException(String message) {
        super(message);
    }

    @Override
    public String getMessage() {
        return super.getMessage();
    }
}
