package ru.itmo.movie.service;

public class Problem extends RuntimeException {
    public final int status;
    public final String code;
    public Integer recordNumber;
    public String path;
    public Long operationId;
    public String operationStatus = "FAILED";

    public Problem(int status, String message) {
        this(status, status == 409 ? "VERSION_CONFLICT" : "INVALID_INPUT", message);
    }

    public Problem(int status, String code, String message) {
        super(message);
        this.status = status;
        this.code = code;
    }

    public Problem at(int record, String field) { recordNumber = record; path = field; return this; }

    public java.util.Map<String, Object> body() {
        var data = new java.util.LinkedHashMap<String, Object>();
        data.put("error", getMessage()); data.put("code", code);
        if (recordNumber != null) data.put("recordNumber", recordNumber);
        if (path != null) data.put("path", path);
        if (operationId != null) { data.put("operationId", operationId.toString()); data.put("status", operationStatus); }
        return data;
    }
}
