import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:craftshood_ai/core/api/api_client.dart';
import 'package:craftshood_ai/core/api/generation_service.dart';
import 'package:craftshood_ai/features/generation/generation_controller.dart';

void main() {
  group('GenerationController', () {
    test('initial state is idle', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);
      final state = container.read(generationControllerProvider);
      expect(state.state, GenerationState.idle);
    });
  });

  group('ApiClient', () {
    test('constructs with default base URL', () {
      final client = ApiClient();
      expect(client.baseUrl, 'http://localhost:8000');
    });
  });
}
