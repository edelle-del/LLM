package com.example.llm.api;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

@Service
public class LlmGenerationService {

    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final String djangoBaseUrl;
    private final String djangoGeneratePath;

    public LlmGenerationService(
            ObjectMapper objectMapper,
            @Value("${django.api.base-url}") String djangoBaseUrl,
            @Value("${django.api.generate-path}") String djangoGeneratePath
    ) {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        this.objectMapper = objectMapper;
        this.djangoBaseUrl = djangoBaseUrl;
        this.djangoGeneratePath = djangoGeneratePath;
    }

    public String generate(String prompt) {
        String safePrompt = prompt == null ? "" : prompt;

        try {
            String requestBody = objectMapper.writeValueAsString(new PromptRequest(safePrompt));
            URI uri = buildEndpointUri(djangoBaseUrl, djangoGeneratePath);

            HttpRequest request = HttpRequest.newBuilder(uri)
                    .header("Content-Type", "application/json")
                    .timeout(Duration.ofSeconds(30))
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_GATEWAY,
                        "Django LLM service request failed with status " + response.statusCode()
                );
            }

            JsonNode root = objectMapper.readTree(response.body());
            JsonNode resultNode = root.path("result");
            if (resultNode.isMissingNode() || resultNode.isNull()) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Django LLM service returned no result field");
            }

            return resultNode.asText();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Error calling Django LLM service", e);
        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Error calling Django LLM service", e);
        }
    }

    private URI buildEndpointUri(String baseUrl, String path) {
        String safeBaseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        String safePath = path.startsWith("/") ? path : "/" + path;
        return URI.create(safeBaseUrl + safePath);
    }
}