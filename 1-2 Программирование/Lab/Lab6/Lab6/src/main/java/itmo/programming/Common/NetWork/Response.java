package itmo.programming.Common.NetWork;

import java.io.Serial;
import java.io.Serializable;

public class Response implements Serializable {
    @Serial
    private static final long serialVersionUID = 6371468372929910569L;
    private String message;
    private String collectionToStr;

    public Response(String message, String collectionToStr) {
        this.message = message;
        this.collectionToStr = collectionToStr
                != null ? collectionToStr : "";
    }


    public Response() {
    }

    /**
     * 获取
     *
     * @return message
     */
    public String getMessage() {
        return message;
    }

    /**
     * 设置
     *
     * @param message
     */
    public void setMessage(String message) {
        this.message = message;
    }

    /**
     * 获取
     *
     * @return collectionToStr
     */
    public String getCollectionToStr() {
        return collectionToStr;
    }

    /**
     * 设置
     *
     * @param collectionToStr
     */
    public void setCollectionToStr(String collectionToStr) {
        this.collectionToStr = collectionToStr;
    }

    public String toString() {
        return "Response{message = " + message + ", collectionToStr = " + collectionToStr + "}";
    }
}
