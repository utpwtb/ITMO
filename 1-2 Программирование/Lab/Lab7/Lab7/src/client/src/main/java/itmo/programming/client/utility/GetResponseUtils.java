package itmo.programming.client.utility;

import itmo.programming.client.manager.NetWorkManager;
import itmo.programming.common.network.Request;
import itmo.programming.common.network.Response;
import java.io.IOException;

/**
 * Утилиты для обработки запросов клиента и ответов сервера.
 */
public class GetResponseUtils {
    
    /**
     * Отправка запроса и получение ответа.
     *
     * @param request объект запроса
     * @param netWorkManager сетевой менеджер
     * @return объект ответа, или null при ошибке
     * @throws IOException сетевая ошибка
     */
    public static Response getResponse(Request request, NetWorkManager netWorkManager) 
            throws IOException {
        final byte[] serializered = netWorkManager.serializer(request);
        if (serializered == null) {
            System.out.println("Ошибка сериализации запроса");
            return null;
        }
        
        // 检查发送是否成功
        if (!netWorkManager.send(serializered)) {
            System.out.println("Не удалось отправить запрос на сервер");
            return null;
        }

        // Ожидание ответа сервера
        final byte[] bytes = netWorkManager.runClientEventLoop();
        if (bytes == null) {
            System.out.println("Сервер не отвечает");
            return null;
        }

        // Разбор ответа сервера
        final Response response = netWorkManager.deserialize(bytes);
        if (response == null) {
            System.out.println("Невозможно разобрать ответ сервера");
            return null;
        }

        return response;
    }
    
    /**
     * Обработка и отображение результатов выполнения скрипта.
     *
     * @param response объект ответа выполнения скрипта
     */
    public static void displayScriptExecutionResponse(Response response) {
        if (response == null) {
            System.out.println("Ошибка выполнения скрипта: не получен ответ");
            return;
        }
        
        System.out.println("===== Результаты выполнения скрипта =====");
        System.out.println(response.getMessage());
        
        if (response.getCollectionToStr() != null && !response.getCollectionToStr().isEmpty()) {
            System.out.println("\nПодробные результаты:");
            System.out.println(response.getCollectionToStr());
        }
        System.out.println("========================================");
    }
}
