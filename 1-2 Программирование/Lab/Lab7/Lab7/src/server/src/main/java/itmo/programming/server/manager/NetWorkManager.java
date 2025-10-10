package itmo.programming.server.manager;

import itmo.programming.common.network.Request;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Менеджер сетевого взаимодействия, обеспечивающий обмен данными между клиентом и сервером.
 * Реализован с использованием блокирующего ввода-вывода.
 */
public class NetWorkManager {

    /**
     * Логгер для записи информации о сетевых операциях.
     */
    public static Logger logger;
    
    /**
     * Размер буфера для чтения/записи данных.
     */
    private static final int BUFFER_SIZE = 4096;
    
    /**
     * Время ожидания для операций ввода-вывода (мс).
     */
    private static final int SOCKET_TIMEOUT = 1000;
    
    /**
     * Максимальный размер данных в байтах.
     */
    private static final int MAX_DATA_SIZE = 1024 * 1024;
    
    /**
     * Серверный сокет для приема подключений.
     */
    private ServerSocket serverSocket;
    
    /**
     * Текущий активный сокет клиента.
     */
    private Socket currentClientSocket;
    
    /**
     * Порт, на котором работает сервер.
     */
    private int port;

    /**
     * Конструктор по умолчанию.
     */
    public NetWorkManager() {
    }

    /**
     * Конструктор с указанием порта.
     *
     * @param port порт для прослушивания
     */
    public NetWorkManager(int port) {
        this.port = port;
        logger = Logger.getLogger(NetWorkManager.class.getName());
    }

    /**
     * Инициализирует сетевой менеджер, открывает серверный сокет.
     *
     * @return true, если инициализация прошла успешно, иначе false
     */
    public boolean init() {
        try {
            serverSocket = new ServerSocket(port);
            serverSocket.setSoTimeout(SOCKET_TIMEOUT);
            logger.info("Сервер запущен на порту: " + port);
            return true;
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Ошибка инициализации сервера: " + e.getMessage(), e);
            return false;
        }
    }

    /**
     * Сериализует объект в массив байтов.
     *
     * @param obj объект для сериализации
     * @return массив байтов или null в случае ошибки
     */
    public byte[] serializer(Object obj) {
        try {
            final ByteArrayOutputStream bos = new ByteArrayOutputStream();
            final ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(obj);
            oos.flush();
            oos.close();
            final byte[] objBytes = bos.toByteArray();
            logger.info("Ответ успешно сериализован! Размер: " + objBytes.length + " байт");
            return objBytes;
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Ошибка сериализации: " + e.getMessage(), e);
            return null;
        }
    }

    /**
     * Десериализует массив байтов в объект Request.
     *
     * @param bytes массив байтов для десериализации
     * @return объект Request или null в случае ошибки
     */
    public Request deserialize(byte[] bytes) {
        if (bytes == null) {
            logger.warning("Попытка десериализации null данных");
            return null;
        }
        try {
            final ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
            final ObjectInputStream ois = new ObjectInputStream(bis);
            final Object obj = ois.readObject();
            if (obj instanceof Request) {
                logger.info("Команда успешно десериализована!");
                return (Request) obj;
            } else {
                logger.warning("Десериализованный объект не является экземпляром Request");
                return null;
            }
        } catch (IOException | ClassNotFoundException e) {
            logger.log(Level.SEVERE, "Не удалось десереализовать объект: " + e.getMessage(), e);
            return null;
        }
    }

    /**
     * Отправляет данные клиенту.
     *
     * @param data данные для отправки
     * @throws IOException в случае ошибки ввода-вывода
     */
    public void send(byte[] data) throws IOException {
        if (data == null) {
            logger.warning("Попытка отправить пустые данные");
            return;
        }
        if (currentClientSocket == null || currentClientSocket.isClosed()) {
            logger.warning("Нет активного соединения с клиентом");
            return;
        }

        try {
            final DataOutputStream dos = new DataOutputStream(
                    currentClientSocket.getOutputStream());
            
            dos.writeInt(data.length);
            
            dos.write(data);
            dos.flush();
            
            logger.info("Данные отправлены клиенту, размер: " + data.length + " байт");
        } catch (IOException e) {
            logger.log(Level.WARNING, "Ошибка при отправке данных: " + e.getMessage(), e);
            closeConnection();
            throw e;
        }
    }

    /**
     * Получает данные от клиента.
     *
     * @return полученные данные или null в случае ошибки или отсутствия данных
     * @throws IOException в случае ошибки ввода-вывода
     */
    private byte[] receive() throws IOException, SocketTimeoutException {
        if (currentClientSocket == null || currentClientSocket.isClosed()) {
            logger.warning("Нет активного соединения с клиентом");
            return null;
        }

        try {
            final DataInputStream dis = new DataInputStream(currentClientSocket.getInputStream());
            final int len = 4;
            final byte[] lengthBytes = new byte[len];
            dis.readFully(lengthBytes);
            final ByteBuffer lengthBuffer = ByteBuffer.wrap(lengthBytes);
            lengthBuffer.order(java.nio.ByteOrder.BIG_ENDIAN); // 使用网络字节序
            final int dataLength = lengthBuffer.getInt();
            
            logger.info("Получен размер данных: " + dataLength + " байт");
            
            if (dataLength <= 0 || dataLength > MAX_DATA_SIZE) {
                logger.warning("Получен некорректный размер данных: " + dataLength);
                return null;
            }

            final byte[] data = new byte[dataLength];
            dis.readFully(data);
            
            logger.info("Получены данные от клиента: " + data.length + " байт");
            return data;
        } catch (SocketTimeoutException e) {
            throw e;
        } catch (SocketException e) {
            logger.info("Соединение с клиентом разорвано: " + e.getMessage());
            closeConnection();
            return null;
        } catch (IOException e) {
            logger.log(Level.WARNING, "Ошибка при получении данных: " + e.getMessage(), e);
            closeConnection();
            throw e;
        }
    }

    /**
     * Принимает новое клиентское подключение.
     *
     * @return true если подключение принято, false если таймаут или ошибка
     * @throws IOException в случае ошибки ввода-вывода
     */
    private boolean acceptConnection() throws IOException {
        try {
            if (currentClientSocket != null && !currentClientSocket.isClosed()) {
                closeConnection();
            }
            
            currentClientSocket = serverSocket.accept();
            currentClientSocket.setSoTimeout(SOCKET_TIMEOUT);
            
            logger.info("Новое подключение: "
                    +
                    currentClientSocket.getInetAddress()
                    +
                    ":" + currentClientSocket.getPort());
            
            try {
                final String welcomeMessage = "Введите «help», чтобы увидеть доступные команды.";
                final DataOutputStream dos = new DataOutputStream(
                        currentClientSocket.getOutputStream());
                final byte[] messageBytes = welcomeMessage.getBytes(StandardCharsets.UTF_8);
                dos.writeInt(messageBytes.length);
                dos.write(messageBytes);
                dos.flush();
                logger.info("Приветственное сообщение отправлено клиенту");
            } catch (IOException e) {
                logger.warning("Не удалось отправить приветственное сообщение: " + e.getMessage());
            }
            
            return true;
        } catch (SocketTimeoutException e) {
            return false;
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Ошибка при принятии подключения: " + e.getMessage(), e);
            throw e;
        }
    }

    /**
     * Выполняет один цикл обработки событий сервера.
     *
     * @return данные запроса или null, если запросов нет
     * @throws IOException в случае ошибки ввода-вывода
     */
    public RequestData runServerEventLoop() throws IOException {
        try {
            if (currentClientSocket == null || currentClientSocket.isClosed()) {
                final boolean accepted = acceptConnection();
                if (!accepted) {
                    return null;
                }
                return null;
            }
            
            try {
                final byte[] received = receive();
                if (received != null) {
                    return new RequestData(received);
                }
                return null;
            } catch (SocketTimeoutException e) {
                logger.fine("Таймаут при ожидании данных от клиента");
                return null;
            }
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Критическая ошибка в цикле событий: " + e.getMessage(), e);
            throw e;
        }
    }

    /**
     * Закрывает соединение с клиентом.
     */
    private void closeConnection() {
        try {
            if (currentClientSocket != null && !currentClientSocket.isClosed()) {
                currentClientSocket.close();
                currentClientSocket = null;
                logger.info("Соединение с клиентом закрыто");
            }
        } catch (IOException ex) {
            logger.log(Level.WARNING, "Ошибка при закрытии соединения: " + ex.getMessage(), ex);
        }
    }

    /**
     * Возвращает порт, на котором работает сервер.
     *
     * @return номер порта
     */
    public int getPort() {
        return this.port;
    }

    /**
     * Возвращает текущий активный сокет клиента.
     *
     * @return текущий активный сокет клиента
     */
    public Socket getCurrentClientSocket() {
        return this.currentClientSocket;
    }

    /**
     * Класс для хранения данных запроса.
     */
    public static class RequestData {
        
        /**
         * Данные запроса.
         */
        public byte[] data;

        /**
         * Конструктор для создания объекта данных запроса.
         *
         * @param data данные запроса
         */
        public RequestData(byte[] data) {
            this.data = data;
        }
    }
}
