package com.campus.assistant.server.utils;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Calendar;

/**
 * 时间工具类
 */
public class DateUtils extends org.apache.commons.lang3.time.DateUtils {
    public static String YYYY = "yyyy";

    public static String YYYY_MM = "yyyy-MM";

    public static String YYYY_MM_DD = "yyyy-MM-dd";

    public static String YYYYMMDDHHMMSS = "yyyyMMddHHmmss";

    public static String YYYY_MM_DD_HH_MM_SS = "yyyy-MM-dd HH:mm:ss";

    public static String YYYY_MM_DD_HH_MM = "yyyy-MM-dd HH:mm";

    private static String[] parsePatterns = {
            "yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd HH:mm", "yyyy-MM",
            "yyyy/MM/dd", "yyyy/MM/dd HH:mm:ss", "yyyy/MM/dd HH:mm", "yyyy/MM",
            "yyyy.MM.dd", "yyyy.MM.dd HH:mm:ss", "yyyy.MM.dd HH:mm", "yyyy.MM"};

    /**
     * 当前时间
     *
     * @return LocalDateTime
     */
    public static LocalDateTime nowTime() {
        return LocalDateTime.now(ZoneId.of("Asia/Shanghai"));
    }

    public static String formatDateTimeToMinute(LocalDateTime time) {
        DateTimeFormatter df = DateTimeFormatter.ofPattern(YYYY_MM_DD_HH_MM);
        return df.format(time);
    }

    /**
     * 当前日期
     *
     * @return LocalDate
     */
    public static LocalDate nowDate() {
        return LocalDate.now(ZoneId.of("Asia/Shanghai"));
    }

    /**
     * 获取上个月天数
     *
     * @return
     */
    public static int lastMonthDayNum() {
        Calendar cal = Calendar.getInstance();
        cal.set(Calendar.DAY_OF_MONTH, 1);
        cal.add(Calendar.DAY_OF_MONTH, -1);
        return cal.get(Calendar.DAY_OF_MONTH);
    }

    public static LocalDateTime parseLocalDateTime(String time) {
        DateTimeFormatter df = DateTimeFormatter.ofPattern(YYYY_MM_DD_HH_MM_SS);
        return LocalDateTime.parse(time, df);
    }

    public static String formatLocalDateTime(LocalDateTime time) {
        DateTimeFormatter df = DateTimeFormatter.ofPattern(YYYY_MM_DD_HH_MM_SS);
        return df.format(time);
    }

    public static String formatLocalDateTimeToDate(LocalDateTime time) {
        DateTimeFormatter df = DateTimeFormatter.ofPattern(YYYY_MM_DD);
        return df.format(time);
    }

    public static LocalDateTime formatLongToLocalDateTime(Long time) {
        return Instant.ofEpochMilli(time).atZone(ZoneId.of("Asia/Shanghai")).toLocalDateTime();
    }
}