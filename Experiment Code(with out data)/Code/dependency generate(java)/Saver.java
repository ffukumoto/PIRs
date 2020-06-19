package com.HDU;

import java.io.*;
import java.util.*;

public class Saver {

    public static void saveStrList(String filename, ArrayList<String> strList){
        StringBuffer writeStrBuffer = new StringBuffer();
        for (String str: strList) {
            writeStrBuffer.append(str);
            writeStrBuffer.append("\n");
        }
        String writeStr = writeStrBuffer.toString();
        saveString(filename, writeStr);
    }

    public static void saveString(String filename, String data){
        try{ // 防止文件建立或读取失败，用catch捕捉错误并打印，也可以throw
            /* 写入Txt文件 */
            String encoding = "utf-8";
            File file = new File(filename); // 相对路径，如果没有则要建立一个新的output。txt文件
            if(file.exists())
                if(!file.delete())
                    throw new RuntimeException("delete error");
            if(file.createNewFile()) {// 创建新文件
                BufferedWriter out = new BufferedWriter(new OutputStreamWriter(
                        new FileOutputStream(file), encoding));
                out.write(data); // \r\n即为换行
//                out.flush(); // 把缓存区内容压入文件
                out.close(); // 最后记得关闭文件
            }
            else
                throw new RuntimeException("create error");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
