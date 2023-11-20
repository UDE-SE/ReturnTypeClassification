public class currentFile { 
    public static void main(String[] args){ 
        System.out.println("Ausgabe aus der main()-Methode"); 
    } 

    public static boolean test(String[] args){ 
        System.out.println("Ausgabe aus der test()-Methode"); 
        return true;
    } 

    public static boolean test(String[] args, String[] args2){ 
        System.out.println("Ausgabe aus der 2. test()-Methode"); 
        return true;
    } 
}