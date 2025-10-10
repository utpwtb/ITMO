import java.util.Random;

public class ThreeArr {
    long[] a;
    double[] x;
    double[][] e;


    public ThreeArr(int zLength, int xLength) {
        a = new long[zLength];
        x = new double[xLength];
        e = new double[zLength][xLength];
    }

    public void fillArrA(int from, int to) {
        for (int i = 0; i < a.length; i++) {
            if (a[i] <= to){
                a[i] = from;
                from += 2;
            }
        }
    }

    public void fillArrX() {
        Random r = new Random();
        for (int i = 0; i < x.length; i++) {
            x[i] = r.nextDouble(27) - 13;
        }
    }

    public void fillArrE() {
        for (int i = 0; i < a.length; i++) {
            for (int j = 0; j < x.length; j++) {
                /*if (a[i] == 10) {
                    e[i][j] = Math.sin(Math.pow((1 - Math.sin(x[j])), Math.asin((x[j] + 0.5) / 27)));
                } else if (a[i] == 12 || a[i] == 14 || a[i] == 16 || a[i] == 18) {
                    e[i][j] = Math.pow((2 * Math.pow((2 * Math.pow(Math.E, x[i])), 2)), 3);
                } else {
                    e[i][j] = Math.asin(Math.pow((1 / (Math.pow(Math.E, (Math.acos(((x[j] + 0.5) / 27)))) / Math.PI) / 2), 2));
                }*/
                switch ((int) a[i]){
                   case 10 -> e[i][j] = Math.sin(Math.pow((1 - Math.sin(x[j])), Math.asin((x[j] + 0.5) / 27)));
                   case 12,14,16,18 ->  e[i][j] = Math.pow((2 * Math.pow((2 * Math.pow(Math.E, x[i])), 2)), 3);
                    default -> e[i][j] = Math.asin(Math.pow((1 / (Math.pow(Math.E, (Math.acos(((x[j] + 0.5) / 27)))) / Math.PI) / 2), 2));
                }
            }

        }
    }

    public void printArrE() {
        for (int i = 0; i < a.length; i++) {
            for (int j = 0; j < x.length; j++) {
                System.out.printf("%.2f ", x[j]);
            }
            System.out.println();
        }
    }
}
