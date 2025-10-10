package itmo.programming.Client.manager;

import itmo.programming.Common.NetWork.Response;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;

public class NetWorkManager {
    private static final int BUFFER_SIZE = 4096;
    private static SocketChannel channel;
    Selector selector;
    private String host;
    private int port;


    public NetWorkManager() {
    }

    public NetWorkManager(String host, int port) {
        this.host = host;
        this.port = port;
    }

    public boolean init(String host, int port) {
        try {
            channel = SocketChannel.open(new InetSocketAddress(host, port));
            selector = Selector.open();
            channel.configureBlocking(false);
            channel.register(selector, SelectionKey.OP_READ);
            System.out.println("Подключение к серверу " + host + ":" + port + " успешно установлено");
            return true;
        } catch (IOException e) {
            System.out.println("Ошибка подключения к серверу: " + e.getMessage());
            return false;
        }
    }

    public byte[] serializer(Object obj) {
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(obj);
            oos.flush();
            oos.close();
            byte[] objBytes = bos.toByteArray();
            return objBytes;
        } catch (IOException e) {
            System.out.println("Ошибка сериализации объекта: " + e.getMessage());
            return null;
        }
    }

    public Response deserialize(byte[] bytes) {
        if (bytes == null) {
            return null;
        }
        try {
            ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
            ObjectInputStream ois = new ObjectInputStream(bis);
            Object obj = ois.readObject();
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

    public void send(byte[] data) {
        if (data == null) {
            return;
        }

        try {
            // 写入数据长度前缀，便于服务器读取完整数据
            ByteBuffer lengthBuffer = ByteBuffer.allocate(4);
            lengthBuffer.putInt(data.length);
            lengthBuffer.flip();
            channel.write(lengthBuffer);

            // 写入实际数据
            ByteBuffer dataBuffer = ByteBuffer.wrap(data);
            while (dataBuffer.hasRemaining()) {
                channel.write(dataBuffer);
            }

        } catch (IOException e) {
            System.out.println("Ошибка при отправке данных: " + e.getMessage());
        }
    }

    public byte[] receiveWelcomeMessage() throws IOException {
        // 接收服务器发送的欢迎消息
        ByteBuffer buffer = ByteBuffer.allocate(BUFFER_SIZE);
        int bytesRead = channel.read(buffer);
        if (bytesRead > 0) {
            buffer.flip();
            byte[] welcomeBytes = new byte[buffer.remaining()];
            buffer.get(welcomeBytes);
            return welcomeBytes;
        }
        return null;
    }

    public byte[] receive(SelectionKey key) {
        try {
            // 首先读取长度前缀
            ByteBuffer lengthBuffer = ByteBuffer.allocate(4);
            int totalRead = 0;
            while (totalRead < 4) {
                int bytesRead = channel.read(lengthBuffer);
                if (bytesRead == -1) {
                    System.out.println("Сервер закрыл соединение");
                    return null;
                } else if (bytesRead == 0) {
                    // 在非阻塞模式下，可能暂时没有数据可读
                    try {
                        Thread.sleep(100); // 短暂休眠避免CPU占用
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    continue;
                }
                totalRead += bytesRead;
            }

            // 解析数据长度
            lengthBuffer.flip();
            int dataLength = lengthBuffer.getInt();


            // 读取实际数据
            ByteBuffer dataBuffer = ByteBuffer.allocate(dataLength);
            totalRead = 0;
            while (totalRead < dataLength) {
                int bytesRead = channel.read(dataBuffer);
                if (bytesRead == -1) {

                    return null;
                } else if (bytesRead == 0) {
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    continue;
                }
                totalRead += bytesRead;
            }

            dataBuffer.flip();
            byte[] data = new byte[dataBuffer.remaining()];
            dataBuffer.get(data);

            return data;
        } catch (IOException e) {
            System.out.println("Ошибка при получении данных: " + e.getMessage());
            return null;
        }
    }

    public byte[] runClientEventLoop() {
        try {
            while (true) {
                int readyChannels = selector.select(5000); // 5秒超时
                if (readyChannels == 0) {

                    return null;
                }

                Set<SelectionKey> selectedKeys = selector.selectedKeys();
                Iterator<SelectionKey> iterator = selectedKeys.iterator();

                while (iterator.hasNext()) {
                    SelectionKey key = iterator.next();
                    iterator.remove();

                    if (!key.isValid()) continue;
                    if (key.isReadable()) {
                        byte[] received = receive(key);
                        return received;
                    }
                }
            }
        } catch (IOException e) {
            System.out.println("Критическая ошибка в цикле событий: " + e.getMessage());
        }
        return null;
    }
}
