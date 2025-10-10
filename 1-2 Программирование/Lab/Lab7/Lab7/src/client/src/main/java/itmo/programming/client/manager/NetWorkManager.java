package itmo.programming.client.manager;

import itmo.programming.common.network.Response;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;

/**
 * Менеджер сетевого взаимодействия на стороне клиента.
 * Обеспечивает подключение к серверу, отправку и получение данных.
 */
public class NetWorkManager {
    private static final int BUFFER_SIZE = 4096;
    private static final int TIME_OUT = 5000;
    private static final int RECONNECT_ATTEMPTS = 5;
    private static final int RECONNECT_DELAY = 2000; // 2 секунды между попытками
    private static SocketChannel channel;
    Selector selector;
    private String host;
    private int port;

    /**
     * Конструктор по умолчанию.
     */
    public NetWorkManager() {
    }

    /**
     * Конструктор с указанием хоста и порта.
     *
     * @param host хост сервера
     * @param port порт сервера
     */
    public NetWorkManager(String host, int port) {
        this.host = host;
        this.port = port;
    }

    /**
     * Проверяет, установлено ли соединение с сервером.
     *
     * @return true, если соединение активно, иначе false
     */
    public boolean isConnected() {
        return channel != null && channel.isOpen();
    }

    /**
     * Инициализирует подключение к серверу.
     *
     * @param host хост сервера
     * @param port порт сервера
     * @return true, если подключение успешно установлено, иначе false
     */
    public boolean init(String host, int port) {
        this.host = host;
        this.port = port;
        return doInit();
    }

    /**
     * Внутренний метод для инициализации соединения.
     *
     * @return true, если подключение успешно установлено, иначе false
     */
    private boolean doInit() {
        try {
            // 确保之前的资源已关闭
            close();
            
            channel = SocketChannel.open(new InetSocketAddress(host, port));
            selector = Selector.open();
            channel.configureBlocking(false);
            channel.register(selector, SelectionKey.OP_READ);
            System.out.println("Подключение к серверу " + host
                    +
                    ":" + port + " успешно установлено");
            return true;
        } catch (IOException e) {
            System.out.println("Ошибка подключения к серверу: " + e.getMessage());
            return false;
        }
    }

    /**
     * Пытается восстановить соединение с сервером.
     *
     * @return true, если соединение успешно восстановлено, иначе false
     */
    public boolean reconnect() {
        System.out.println("Попытка восстановить соединение с сервером...");
        int attempts = 0;
        
        while (attempts < RECONNECT_ATTEMPTS) {
            attempts++;
            System.out.println("Попытка " + attempts + " из " + RECONNECT_ATTEMPTS);
            
            if (doInit()) {
                System.out.println("Соединение с сервером восстановлено.");
                return true;
            }
            
            // 等待一段时间后重试
            try {
                Thread.sleep(RECONNECT_DELAY);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        System.out.println("Не удалось восстановить соединение с сервером после "
                +
                RECONNECT_ATTEMPTS + " попыток.");
        return false;
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
            return objBytes;
        } catch (IOException e) {
            System.out.println("Ошибка сериализации объекта: " + e.getMessage());
            return null;
        }
    }

    /**
     * Десериализует массив байтов в объект Response.
     *
     * @param bytes массив байтов для десериализации
     * @return объект Response или null в случае ошибки
     */
    public Response deserialize(byte[] bytes) {
        if (bytes == null) {
            return null;
        }
        try {
            final ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
            final ObjectInputStream ois = new ObjectInputStream(bis);
            final Object obj = ois.readObject();
            if (obj instanceof Response) {

                return (Response) obj;
            } else {

                return null;
            }
        } catch (IOException | ClassNotFoundException e) {
            System.out.println("Ошибка десериализации: " + e.getMessage());
            return null;
        }
    }

    /**
     * Отправляет данные серверу, с поддержкой
     * автоматического переподключения при потере соединения.
     *
     * @param data массив байтов для отправки
     * @return true, если данные успешно отправлены, иначе false
     */
    public boolean send(byte[] data) {
        if (data == null) {
            return false;
        }

        // Проверяем состояние соединения
        if (!isConnected()) {
            System.out.println("Соединение с сервером потеряно. Пытаемся восстановить...");
            if (!reconnect()) {
                return false;
            }
        }

        try {
            // 写入数据长度前缀，便于服务器读取完整数据
            final ByteBuffer lengthBuffer = ByteBuffer.allocate(4);
            lengthBuffer.order(java.nio.ByteOrder.BIG_ENDIAN); // 使用网络字节序（大端序）
            lengthBuffer.putInt(data.length);
            lengthBuffer.flip();
            channel.write(lengthBuffer);

            // 写入实际数据
            final ByteBuffer dataBuffer = ByteBuffer.wrap(data);
            while (dataBuffer.hasRemaining()) {
                channel.write(dataBuffer);
            }
            
            return true;
        } catch (IOException e) {
            System.out.println("Ошибка при отправке данных: " + e.getMessage());
            // 尝试重连
            System.out.println("Пытаемся восстановить соединение...");
            return reconnect();
        }
    }

    /**
     * Получает приветственное сообщение от сервера.
     *
     * @return массив байтов с сообщением или null в случае ошибки
     * @throws IOException при ошибке чтения данных
     */
    public byte[] receiveWelcomeMessage() throws IOException {
        final int capacity = 4;
        final ByteBuffer lengthBuffer = ByteBuffer.allocate(capacity);
        int totalRead = 0;
        while (totalRead < capacity) {
            final int bytesRead = channel.read(lengthBuffer);
            if (bytesRead == -1) {
                System.out.println("Сервер закрыл соединение");
                return null;
            }
            totalRead += bytesRead;
        }
        
        // 解析数据长度，使用网络字节序（大端序）
        lengthBuffer.flip();
        lengthBuffer.order(java.nio.ByteOrder.BIG_ENDIAN);
        final int messageLength = lengthBuffer.getInt();
        
        // 读取实际消息内容
        final ByteBuffer messageBuffer = ByteBuffer.allocate(messageLength);
        totalRead = 0;
        while (totalRead < messageLength) {
            final int bytesRead = channel.read(messageBuffer);
            if (bytesRead == -1) {
                System.out.println("Сервер закрыл соединение");
                return null;
            }
            totalRead += bytesRead;
        }
        
        messageBuffer.flip();
        final byte[] welcomeBytes = new byte[messageBuffer.remaining()];
        messageBuffer.get(welcomeBytes);
        return welcomeBytes;
    }

    /**
     * Получает данные от сервера.
     *
     * @param key ключ выбора для канала
     * @return массив байтов с данными или null в случае ошибки
     */
    public byte[] receive(SelectionKey key) {
        try {
            // 首先读取长度前缀
            final int len = 4;
            final ByteBuffer lengthBuffer = ByteBuffer.allocate(len);
            int totalRead = 0;
            final int total = 4;
            while (totalRead < total) {
                final int bytesRead = channel.read(lengthBuffer);
                if (bytesRead == -1) {
                    System.out.println("Сервер закрыл соединение");
                    return null;
                } else if (bytesRead == 0) {
                    // 在非阻塞模式下，可能暂时没有数据可读
                    try {
                        final int sleep = 100;
                        Thread.sleep(sleep); // 短暂休眠避免CPU占用
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    continue;
                }
                totalRead += bytesRead;
            }

            // 解析数据长度
            lengthBuffer.flip();
            lengthBuffer.order(java.nio.ByteOrder.BIG_ENDIAN); // 使用网络字节序（大端序）
            final int dataLength = lengthBuffer.getInt();

            // 验证数据长度是否有效
            if (dataLength <= 0 || dataLength > Integer.MAX_VALUE / 2) {
                System.out.println("Ошибка: недопустимая длина данных: " + dataLength);
                return null;
            }

            // 读取实际数据
            final ByteBuffer dataBuffer = ByteBuffer.allocate(dataLength);
            totalRead = 0;
            while (totalRead < dataLength) {
                final int bytesRead = channel.read(dataBuffer);
                if (bytesRead == -1) {

                    return null;
                } else if (bytesRead == 0) {
                    try {
                        final int sleep = 100;
                        Thread.sleep(sleep);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    continue;
                }
                totalRead += bytesRead;
            }

            dataBuffer.flip();
            final byte[] data = new byte[dataBuffer.remaining()];
            dataBuffer.get(data);

            return data;
        } catch (IOException e) {
            System.out.println("Ошибка при получении данных: " + e.getMessage());
            return null;
        }
    }

    /**
     * Выполняет цикл обработки событий клиента.
     *
     * @return массив байтов с данными или null в случае ошибки или таймаута
     */
    public byte[] runClientEventLoop() {
        try {
            // 设置超时时间
            final long startTime = System.currentTimeMillis();
            final long timeout = TIME_OUT;
            
            while (System.currentTimeMillis() - startTime < timeout) {
                final int readyChannels = selector.select(100); // 使用较短的超时检查
                if (readyChannels == 0) {
                    continue; // 继续等待
                }

                final Set<SelectionKey> selectedKeys = selector.selectedKeys();
                final Iterator<SelectionKey> iterator = selectedKeys.iterator();

                while (iterator.hasNext()) {
                    final SelectionKey key = iterator.next();
                    iterator.remove();

                    if (!key.isValid()) {
                        continue;
                    }
                    if (key.isReadable()) {
                        final byte[] received = receive(key);
                        if (received != null && received.length > 0) {
                            // 确保没有其他数据等待读取
                            selector.selectNow(); // 非阻塞检查
                            return received;
                        }
                    }
                }
            }
            
            // 超时，可能是因为连接断开，尝试重连
            if (!isConnected()) {
                System.out.println("Время ожидания ответа превышено. Проверка соединения...");
                reconnect();
            } else {
                System.out.println("Превышено время ожидания ответа от сервера");
            }
            return null;
        } catch (IOException e) {
            System.out.println("Ошибка в цикле событий: " + e.getMessage());
            // 尝试重连
            reconnect();
            return null;
        }
    }

    /**
     * Запускает процесс получения и обработки ответа от сервера.
     * Получает данные, десериализует их и выводит результат.
     */
    public void start() {
        final byte[] bytes = this.runClientEventLoop();
        if (bytes != null) {
            final Response deserialize = this.deserialize(bytes);
            if (deserialize != null) {
                System.out.println(deserialize.getMessage());
                if (deserialize.getCollectionToStr() != null) {
                    System.out.println(deserialize.getCollectionToStr());
                }
            } else {
                System.out.println("Получен неверный ответ от сервера.");
            }
        } else {
            System.out.println("Нет ответа от сервера.");
        }
    }

    /**
     * Закрывает сетевые ресурсы.
     *
     *  @throws IOException при ошибке закрытия ресурсов
     */
    public void close() throws IOException {
        if (channel != null && channel.isOpen()) {
            channel.close();
        }
        if (selector != null && selector.isOpen()) {
            selector.close();
        }
    }
}


