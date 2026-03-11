package com.example.llm.api;

public class GenerationResponse {

    private String result;

    public GenerationResponse() {
    }

    public GenerationResponse(String result) {
        this.result = result;
    }

    public String getResult() {
        return result;
    }

    public void setResult(String result) {
        this.result = result;
    }
}

