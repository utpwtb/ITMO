package itmo.programming.server.utility;

import itmo.programming.common.network.Response;
import itmo.programming.server.manager.NetWorkManager;
import java.io.IOException;
import java.net.Socket;
import java.util.logging.Logger;
/**
 * Класс для отправки ответов клиенту.
 */

public class ResponseSender {

    /**
     * Логгер для записи информации об отправке ответов.
     */
    private static final Logger logger = Logger.getLogger(ResponseSender.class.getName());
    
    /**
     * Менеджер сетевого взаимодействия.
     */
    private final NetWorkManager netWorkManager;

    /**
     * Конструктор класса ResponseSender.
     *
     * @param netWorkManager менеджер сетевого взаимодействия
     */
    public ResponseSender(NetWorkManager netWorkManager) {
        this.netWorkManager = netWorkManager;
    }

    /**
     * Отправляет результат проверки ID клиенту.
     *
     * @param result результат проверки (true - положительный, false - отрицательный)
     * @throws IOException в случае ошибки при отправке ответа
     */
    public void resultJudge(boolean result) throws IOException {
        // Создаем стандартный объект Response
        final Response response = new Response();
        if (result) {
            response.setMessage("T");
            logger.info("Отправка положительного результата проверки ID (T)");
        } else {
            response.setMessage("F");
            logger.info("Отправка отрицательного результата проверки ID (F)");
        }

        // Сериализуем Response с помощью NetWorkManager
        final byte[] serialized = netWorkManager.serializer(response);
        if (serialized == null) {
            logger.warning("Не удалось сериализовать ответ");
            return;
        }

        final Socket currentClientSocket = netWorkManager.getCurrentClientSocket();
        if (currentClientSocket != null && !currentClientSocket.isClosed()) {
            netWorkManager.send(serialized);
            logger.info("Ответ успешно отправлен клиенту");
        } else {
            logger.warning("Невозможно отправить ответ: нет активных клиентских подключений");
            throw new IOException(
                    "Невозможно отправить ответ: "
                            +
                            "в настоящее время нет активных клиентских подключений.");
        }
    }
}
