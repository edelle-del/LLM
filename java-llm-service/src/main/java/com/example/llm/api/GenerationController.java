package com.example.llm.api;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@CrossOrigin(origins = "*")
@RequestMapping(path = "/llm", produces = MediaType.APPLICATION_JSON_VALUE)
public class GenerationController {

    private final LlmGenerationService llmGenerationService;

    public GenerationController(LlmGenerationService llmGenerationService) {
        this.llmGenerationService = llmGenerationService;
    }

    @PostMapping(path = "/generate", consumes = MediaType.APPLICATION_JSON_VALUE)
    public GenerationResponse generate(@RequestBody PromptRequest request) {
        String result = llmGenerationService.generate(request.getPrompt());
        return new GenerationResponse(result);
    }
}

