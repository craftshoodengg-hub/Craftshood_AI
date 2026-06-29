import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'endpoints.dart';

class ApiClient {
  final http.Client _client;
  final String baseUrl;

  ApiClient({http.Client? client, this.baseUrl = ApiEndpoints.baseUrl})
      : _client = client ?? http.Client();

  Future<Map<String, dynamic>> get(String path) async {
    final uri = _resolveUri(path);
    try {
      final response = await _client.get(uri).timeout(const Duration(seconds: 10));
      return _handleResponse(response);
    } on SocketException {
      throw const ApiException('Server unavailable. Please check your connection.');
    } on http.ClientException {
      throw const ApiException('Network error. Please try again.');
    }
  }

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    final uri = _resolveUri(path);
    try {
      final response = await _client
          .post(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode(body))
          .timeout(const Duration(seconds: 30));
      return _handleResponse(response);
    } on SocketException {
      throw const ApiException('Server unavailable. Please check your connection.');
    } on http.ClientException {
      throw const ApiException('Network error. Please try again.');
    }
  }

  Uri _resolveUri(String path) {
    if (path.startsWith('http')) return Uri.parse(path);
    var base = baseUrl;
    if (base.endsWith('/') && path.startsWith('/')) {
      base = base.substring(0, base.length - 1);
    } else if (!base.endsWith('/') && !path.startsWith('/')) {
      base = '$base/';
    }
    return Uri.parse('$base$path');
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }
    throw ApiException(body['detail'] ?? body['error'] ?? 'Server error (${response.statusCode})');
  }

  void dispose() => _client.close();
}

class ApiException implements Exception {
  final String message;
  const ApiException(this.message);
  @override
  String toString() => message;
}
