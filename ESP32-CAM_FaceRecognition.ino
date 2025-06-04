/*
 * ESP32-CAM Face Recognition Stream Server
 * Compatible avec le système de reconnaissance faciale Python
 * 
 * Configuration requise:
 * - Carte: AI Thinker ESP32-CAM
 * - Partition Scheme: Huge APP (3MB No OTA/1MB SPIFFS)
 * 
 * Connexions:
 * - IO0 à GND pour la programmation (déconnecter après upload)
 * - Utiliser un programmeur FTDI pour l'upload
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"

// Configuration de la caméra AI Thinker ESP32-CAM
#define CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Configuration Wi-Fi - MODIFIEZ CES VALEURS
const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_MOT_DE_PASSE";

// Configuration du serveur
httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

// LED Flash (GPIO 4)
#define FLASH_LED_PIN 4
bool flashState = false;

// Variables de performance
unsigned long lastFrameTime = 0;
int frameCount = 0;
float fps = 0;

static const char PROGMEM INDEX_HTML[] = R"rawliteral(
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>ESP32-CAM Face Recognition</title>
    <style>
        body { font-family: Arial; text-align: center; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .stream-container { margin: 20px 0; }
        img { max-width: 100%; height: auto; border: 2px solid #333; }
        .controls { margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; }
        .info { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-CAM Face Recognition</h1>
        <div class="info">
            <p><strong>IP:</strong> <span id="ip"></span></p>
            <p><strong>Statut:</strong> <span id="status">Connecté</span></p>
            <p><strong>FPS:</strong> <span id="fps">--</span></p>
        </div>
        <div class="stream-container">
            <img id="stream" src="/stream" style="display: none;">
        </div>
        <div class="controls">
            <button onclick="toggleFlash()">Toggle Flash</button>
            <button onclick="restartCamera()">Redémarrer Caméra</button>
            <button onclick="location.reload()">Actualiser</button>
        </div>
    </div>
    
    <script>
        document.getElementById('ip').textContent = window.location.hostname;
        
        const streamImg = document.getElementById('stream');
        streamImg.onload = function() {
            this.style.display = 'block';
        };
        
        function toggleFlash() {
            fetch('/flash')
                .then(response => response.text())
                .then(data => console.log(data));
        }
        
        function restartCamera() {
            fetch('/restart')
                .then(response => response.text())
                .then(data => {
                    console.log(data);
                    setTimeout(() => location.reload(), 2000);
                });
        }
        
        // Mise à jour du FPS
        setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('fps').textContent = data.fps.toFixed(1);
                });
        }, 2000);
    </script>
</body>
</html>
)rawliteral";

static esp_err_t index_handler(httpd_req_t *req) {
    httpd_resp_set_type(req, "text/html");
    return httpd_resp_send(req, INDEX_HTML, strlen(INDEX_HTML));
}

static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len = 0;
    uint8_t * _jpg_buf = NULL;
    char * part_buf[128];

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
    if(res != ESP_OK) {
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "X-Framerate", "30");

    while(true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Erreur capture caméra");
            res = ESP_FAIL;
        } else {
            // Calculer FPS
            unsigned long currentTime = millis();
            if (currentTime - lastFrameTime >= 1000) {
                fps = frameCount * 1000.0 / (currentTime - lastFrameTime);
                frameCount = 0;
                lastFrameTime = currentTime;
            }
            frameCount++;

            if(fb->width > 400) {
                if(fb->format != PIXFORMAT_JPEG) {
                    bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
                    esp_camera_fb_return(fb);
                    fb = NULL;
                    if(!jpeg_converted) {
                        Serial.println("Erreur conversion JPEG");
                        res = ESP_FAIL;
                    }
                } else {
                    _jpg_buf_len = fb->len;
                    _jpg_buf = fb->buf;
                }
            }
        }
        
        if(res == ESP_OK) {
            res = httpd_resp_send_chunk(req, "\r\n--frame\r\n", 13);
        }
        if(res == ESP_OK) {
            size_t hlen = snprintf((char *)part_buf, 128, 
                "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", 
                _jpg_buf_len);
            res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
        }
        if(res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
        }
        
        if(fb) {
            esp_camera_fb_return(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if(_jpg_buf) {
            free(_jpg_buf);
            _jpg_buf = NULL;
        }
        
        if(res != ESP_OK) {
            break;
        }
    }
    return res;
}

static esp_err_t flash_handler(httpd_req_t *req) {
    flashState = !flashState;
    digitalWrite(FLASH_LED_PIN, flashState ? HIGH : LOW);
    
    httpd_resp_set_type(req, "text/plain");
    return httpd_resp_send(req, flashState ? "Flash ON" : "Flash OFF", -1);
}

static esp_err_t status_handler(httpd_req_t *req) {
    char json_response[200];
    snprintf(json_response, sizeof(json_response),
        "{\"fps\":%.1f,\"flash\":%s,\"heap\":%d}",
        fps, flashState ? "true" : "false", ESP.getFreeHeap());
    
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, json_response, strlen(json_response));
}

static esp_err_t restart_handler(httpd_req_t *req) {
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_send(req, "Redémarrage en cours...", -1);
    delay(1000);
    ESP.restart();
    return ESP_OK;
}

void startCameraServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;
    config.ctrl_port = 32768;

    httpd_uri_t index_uri = {
        .uri       = "/",
        .method    = HTTP_GET,
        .handler   = index_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t flash_uri = {
        .uri       = "/flash",
        .method    = HTTP_GET,
        .handler   = flash_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t status_uri = {
        .uri       = "/status",
        .method    = HTTP_GET,
        .handler   = status_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t restart_uri = {
        .uri       = "/restart",
        .method    = HTTP_GET,
        .handler   = restart_handler,
        .user_ctx  = NULL
    };

    if (httpd_start(&camera_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(camera_httpd, &index_uri);
        httpd_register_uri_handler(camera_httpd, &flash_uri);
        httpd_register_uri_handler(camera_httpd, &status_uri);
        httpd_register_uri_handler(camera_httpd, &restart_uri);
    }

    config.server_port += 1;
    config.ctrl_port += 1;
    if (httpd_start(&stream_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(stream_httpd, &stream_uri);
    }
}

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
    Serial.println("=== ESP32-CAM Face Recognition Server ===");

    // Configuration du pin LED Flash
    pinMode(FLASH_LED_PIN, OUTPUT);
    digitalWrite(FLASH_LED_PIN, LOW);

    // Configuration de la caméra
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Configuration de la résolution et qualité pour reconnaissance faciale
    if(psramFound()) {
        config.frame_size = FRAMESIZE_VGA;  // 640x480 - optimal pour reconnaissance faciale
        config.jpeg_quality = 10;           // Qualité élevée pour meilleure détection
        config.fb_count = 2;                // Double buffering
        Serial.println("PSRAM trouvé - Configuration haute qualité");
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
        Serial.println("PSRAM non trouvé - Configuration standard");
    }

    // Initialisation de la caméra
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Erreur initialisation caméra: 0x%x\n", err);
        return;
    }

    // Configuration avancée du capteur pour reconnaissance faciale
    sensor_t * s = esp_camera_sensor_get();
    if (s != NULL) {
        // Optimisations pour reconnaissance faciale
        s->set_brightness(s, 0);     // Luminosité normale
        s->set_contrast(s, 0);       // Contraste normal
        s->set_saturation(s, 0);     // Saturation normale
        s->set_special_effect(s, 0); // Pas d'effet spécial
        s->set_whitebal(s, 1);       // Balance des blancs auto
        s->set_awb_gain(s, 1);       // Gain balance blancs auto
        s->set_wb_mode(s, 0);        // Mode balance blancs auto
        s->set_exposure_ctrl(s, 1);  // Contrôle exposition auto
        s->set_aec2(s, 0);           // AEC2 désactivé
        s->set_ae_level(s, 0);       // Niveau exposition auto
        s->set_aec_value(s, 300);    // Valeur exposition
        s->set_gain_ctrl(s, 1);      // Contrôle gain auto
        s->set_agc_gain(s, 0);       // Gain AGC
        s->set_gainceiling(s, (gainceiling_t)0); // Plafond gain
        s->set_bpc(s, 0);            // BPC désactivé
        s->set_wpc(s, 1);            // WPC activé
        s->set_raw_gma(s, 1);        // Raw GMA activé
        s->set_lenc(s, 1);           // Correction lentille activée
        s->set_hmirror(s, 0);        // Miroir horizontal désactivé
        s->set_vflip(s, 0);          // Retournement vertical désactivé
        s->set_dcw(s, 1);            // DCW activé
        s->set_colorbar(s, 0);       // Barre de couleur désactivée

        Serial.println("Configuration capteur optimisée pour reconnaissance faciale");
    }

    // Connexion Wi-Fi
    WiFi.begin(ssid, password);
    WiFi.setSleep(false);

    Serial.print("Connexion Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("WiFi connecté!");

    Serial.print("Adresse IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("URL du flux: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");
    Serial.print("Interface web: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/");

    // Démarrage du serveur
    startCameraServer();

    Serial.println("Serveur ESP32-CAM démarré!");
    Serial.println("Prêt pour la reconnaissance faciale");

    // Clignotement LED pour indiquer que le système est prêt
    for(int i = 0; i < 3; i++) {
        digitalWrite(FLASH_LED_PIN, HIGH);
        delay(200);
        digitalWrite(FLASH_LED_PIN, LOW);
        delay(200);
    }
}

void loop() {
    // Surveillance de la connexion Wi-Fi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Connexion Wi-Fi perdue, tentative de reconnexion...");
        WiFi.begin(ssid, password);

        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 20) {
            delay(500);
            Serial.print(".");
            attempts++;
        }

        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\nReconnexion Wi-Fi réussie!");
        } else {
            Serial.println("\nÉchec de reconnexion, redémarrage...");
            ESP.restart();
        }
    }

    delay(1000);
}
