import '../models/generation_request.dart';
import '../models/generation_result.dart';
import 'api_client.dart';
import 'endpoints.dart';

class GenerationService {
  final ApiClient _client;
  GenerationService(this._client);

  Future<bool> checkHealth() async {
    final response = await _client.get(ApiEndpoints.health);
    return response['status'] == 'ok';
  }

  Future<String> getVersion() async {
    final response = await _client.get(ApiEndpoints.version);
    return response['version'] as String? ?? 'unknown';
  }

  Future<GenerationResult> generate(String prompt) async {
    final response = await _client.post(ApiEndpoints.generate, GenerationRequest(prompt: prompt).toJson());
    return GenerationResult.fromJson(response);
  }
}
