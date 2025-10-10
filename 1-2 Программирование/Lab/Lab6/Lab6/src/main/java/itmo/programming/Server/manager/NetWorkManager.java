package itmo.programming.Server.manager;

import itmo.programming.Common.NetWork.Request;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.charset.Charset;
import java.util.Iterator;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

public class NetWorkManager {
    private static final int BUFFER_SIZE = 4096;
    public static Logger logger;
    Selector selector;
    private ServerSocketChannel serverSocketChannel;
    private int port;

    public NetWorkManager() {
    }

    public NetWorkManager(int port) {
        this.port = port;
        logger = Logger.getLogger(NetWorkManager.class.getName());
    }

    public boolean init() {
        try {
            serverSocketChannel = ServerSocketChannel.open();
            serverSocketChannel.configureBlocking(false);
            serverSocketChannel.bind(new InetSocketAddress(port));
            selector = Selector.open();
            serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
            logger.info("Сервер запущен на порту: " + port);
            return true;
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Ошибка инициализации сервера: " + e.getMessage(), e);
            return false;
        }
    }

    /**
     * Сериализовать объект в массив байтов.
     *
     * @param obj Объекты, которые необходимо сериализовать
     * @return Сериализованный массив байтов
     */
    public byte[] serializer(Object obj) {
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(obj);
            oos.flush();
            oos.close();
            byte[] objBytes = bos.toByteArray();
            logger.info("Ответ успешно сериализован! Размер: " + objBytes.length + " байт");
            return objBytes;
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Ошибка сериализации: " + e.getMessage(), e);
            return null;
        }
    }

    /**
     * Десериализуем массив байтов в объект Request.
     *
     * @param bytes массив байтов
     * @return объект Request
     */
    public Request deserialize(byte[] bytes) {
        if (bytes == null) {
            logger.warning("Попытка десериализации null данных");
            return null;
        }
        try {
            ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
            ObjectInputStream ois = new ObjectInputStream(bis);
            Object obj = ois.readObject();
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
     * Отправка данных.
     *
     * @param key  Выберите ключ
     * @param data Данные для отправки
     * @throws IOException
     */
    public void send(SelectionKey key, byte[] data) throws IOException {
        if (data == null) {
            logger.warning("Попытка отправить пустые данные");
            return;
        }
        if (!key.isValid()) {
            logger.warning("Ключ недействителен");
            return;
        }

        SocketChannel channel = (SocketChannel) key.channel();

        // 发送数据长度前缀
        ByteBuffer lengthBuffer = ByteBuffer.allocate(4);
        lengthBuffer.putInt(data.length);
        lengthBuffer.flip();
        channel.write(lengthBuffer);

        // 发送实际数据
        ByteBuffer dataBuffer = ByteBuffer.wrap(data);
        while (dataBuffer.hasRemaining()) {
            channel.write(dataBuffer);
        }
        logger.info("Данные отправлены клиенту, размер: " + data.length + " байт");
    }

    private byte[] receive(SelectionKey key) throws IOException {
        SocketChannel channel = (SocketChannel) key.channel();

        // 首先读取长度前缀
        ByteBuffer lengthBuffer = ByteBuffer.allocate(4);
        int totalRead = 0;

        while (totalRead < 4) {
            int bytesRead = channel.read(lengthBuffer);
            if (bytesRead == -1) {
                logger.info("Клиент отключен: " + channel.getRemoteAddress());
                closeConnection(key);
                return null;
            } else if (bytesRead == 0) {
                return null; // 暂时没有数据
            }
            totalRead += bytesRead;
        }

        // 解析数据长度
        lengthBuffer.flip();
        int dataLength = lengthBuffer.getInt();
        logger.info("Получен размер данных: " + dataLength + " байт");

        if (dataLength <= 0 || dataLength > 1024 * 1024) { // 防止异常长度
            logger.warning("Получен некорректный размер данных: " + dataLength);
            return null;
        }

        // 读取实际数据
        ByteBuffer dataBuffer = ByteBuffer.allocate(dataLength);
        totalRead = 0;

        while (totalRead < dataLength) {
            int bytesRead = channel.read(dataBuffer);
            if (bytesRead == -1) {
                logger.info("Клиент отключен во время чтения данных: " + channel.getRemoteAddress());
                closeConnection(key);
                return null;
            } else if (bytesRead == 0) {
                // 在非阻塞模式下可能需要多次读取
                continue;
            }
            totalRead += bytesRead;
        }

        dataBuffer.flip();
        byte[] data = new byte[dataBuffer.remaining()];
        dataBuffer.get(data);
        logger.info("Получены данные [" + channel.getRemoteAddress() +
                "]: " + data.length + " байт");
        return data;
    }

    private void accept() throws IOException {
        SocketChannel accept = serverSocketChannel.accept();
        accept.configureBlocking(false);
        accept.register(selector, SelectionKey.OP_READ);
        // 发送欢迎消息
        String welcomeMessage = "Введите «help», чтобы увидеть доступные команды.";
        accept.write(Charset.forName("UTF-8").encode(welcomeMessage));
        logger.info("Новое подключение: " + accept.getRemoteAddress());
    }

    public RequestData runServerEventLoop() throws IOException {
        try {
            while (true) {
                int readChannels = selector.select(1000); // 1秒超时
                if (readChannels == 0) {
                    continue; // 超时继续
                }

                Set<SelectionKey> selectedKeys = selector.selectedKeys();
                Iterator<SelectionKey> iterator = selectedKeys.iterator();

                while (iterator.hasNext()) {
                    SelectionKey key = iterator.next();
                    iterator.remove();

                    try {
                        if (!key.isValid()) continue;

                        if (key.isAcceptable()) {
                            accept();
                        } else if (key.isReadable()) {
                            byte[] received = receive(key);
                            if (received != null) {
                                RequestData requestData = new RequestData(received, key);
                                return requestData;
                            }
                        }
                    } catch (IOException e) {
                        logger.log(Level.SEVERE, "Ошибка обработки события: " + e.getMessage(), e);
                        closeConnection(key);
                    }
                }
            }
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Критическая ошибка в цикле событий: " + e.getMessage(), e);
        }
        return null;
    }

    /**
     * 关闭连接
     */
    private void closeConnection(SelectionKey key) {
        try {
            if (key != null) {
                key.cancel();
                if (key.channel() != null) {
                    key.channel().close();
                }
            }
        } catch (IOException ex) {
            logger.log(Level.WARNING, "Ошибка при закрытии соединения: " + ex.getMessage(), ex);
        }
    }

    public static class RequestData {
        public byte[] data;
        public SelectionKey key;

        public RequestData(byte[] data, SelectionKey key) {
            this.data = data;
            this.key = key;
        }
    }
}
