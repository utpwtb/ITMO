package itmo.programming.client.commandsclient;

import itmo.programming.common.exceptions.ArgumentException;
import itmo.programming.common.network.Request;
import itmo.programming.common.person.HairColor;
import itmo.programming.common.utility.CommandMode;
import itmo.programming.common.utility.EnumUtils;
import java.io.IOException;

/**
 * Класс команды для вывода элементов, у которых значение поля hairColor меньше указанного значения.
 */
public class FilterLessThanHairColorClient extends CommandClient {
    @Override
    public Request execute(String[] args, CommandMode mode) throws IOException {
        validateArgs(args, mode);
        return new Request("filter_less_than_hair_color", args);
    }

    @Override
    public void validateConsoleArgs(String[] args) {
        if (args.length != 1) {
            throw new ArgumentException(
                    "Неправильное количество аргументов!Эта команда имеет "
                            + "и только имеет один аргумент.Пожалуйста, введите:'"
                            + "filter_less_than_hair_color"
                            + " {HairColor}'(Существующие цвета: )"
                            + EnumUtils.showEnum(HairColor.class)
            );
        }
    }

    @Override
    public void validateScriptArgs(String[] args) {
        validateConsoleArgs(args);
    }
}
