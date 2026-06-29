import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';
import '../../core/api/generation_service.dart';
import '../../core/models/generation_result.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
final generationServiceProvider = Provider<GenerationService>((ref) {
  final client = ref.watch(apiClientProvider);
  return GenerationService(client);
});

enum GenerationState { idle, loading, success, error }

class GenerationStateData {
  final GenerationState state;
  final GenerationResult? result;
  final String? errorMessage;
  const GenerationStateData({this.state = GenerationState.idle, this.result, this.errorMessage});
}

class GenerationController extends StateNotifier<GenerationStateData> {
  final GenerationService _service;
  GenerationController(this._service) : super(const GenerationStateData());

  Future<void> generate(String prompt) async {
    if (prompt.trim().isEmpty) {
      state = const GenerationStateData(state: GenerationState.error, errorMessage: 'Please enter a design prompt.');
      return;
    }
    state = const GenerationStateData(state: GenerationState.loading);
    try {
      final result = await _service.generate(prompt);
      state = GenerationStateData(state: GenerationState.success, result: result);
    } catch (e) {
      state = GenerationStateData(state: GenerationState.error, errorMessage: e.toString());
    }
  }

  void reset() => state = const GenerationStateData();
}

final generationControllerProvider = StateNotifierProvider<GenerationController, GenerationStateData>((ref) {
  final service = ref.watch(generationServiceProvider);
  return GenerationController(service);
});
