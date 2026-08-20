import 'package:flutter/material.dart';

import '../services/api_service.dart';

class CamionesPage extends StatefulWidget {
  const CamionesPage({super.key, required this.token});

  final String token;

  @override
  State<CamionesPage> createState() => _CamionesPageState();
}

class _CamionesPageState extends State<CamionesPage> {
  final ApiService apiService = ApiService();

  List<dynamic> camiones = [];
  String? error;
  bool cargando = false;

  @override
  void dispose() {
    super.dispose();
  }

  Future<void> cargarCamiones() async {
    setState(() {
      cargando = true;
      error = null;
    });

    try {
      final resultado = await apiService.obtenerCamiones(widget.token);
      if (!mounted) return;

      setState(() {
        camiones = resultado;
      });
    } catch (exception) {
      if (!mounted) return;

      setState(() {
        error = exception.toString().replaceFirst('Exception: ', '');
        camiones = [];
      });
    } finally {
      if (mounted) {
        setState(() {
          cargando = false;
        });
      }
    }
  }

  String valorCamion(Map<String, dynamic> camion, List<String> claves) {
    for (final clave in claves) {
      final valor = camion[clave];
      if (valor != null && valor.toString().isNotEmpty) {
        return valor.toString();
      }
    }
    return 'Sin información';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Camiones'),
        actions: [
          IconButton(
            onPressed: cargando ? null : cargarCamiones,
            tooltip: 'Actualizar camiones',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: cargando ? null : cargarCamiones,
                icon: cargando
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.local_shipping),
                label: Text(cargando ? 'Consultando...' : 'Consultar camiones'),
              ),
            ),
            const SizedBox(height: 16),
            if (error != null)
              Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
                textAlign: TextAlign.center,
              ),
            if (error == null && !cargando && camiones.isEmpty)
              const Expanded(
                child: Center(
                  child: Text('Aún no hay camiones para mostrar.'),
                ),
              )
            else
              Expanded(
                child: ListView.separated(
                  itemCount: camiones.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = camiones[index];
                    final camion = item is Map
                        ? Map<String, dynamic>.from(item)
                        : <String, dynamic>{};

                    return Card(
                      child: ListTile(
                        leading: const CircleAvatar(
                          child: Icon(Icons.local_shipping),
                        ),
                        title: Text(
                          valorCamion(camion, ['placa', 'Placa', 'matricula', 'id']),
                        ),
                        subtitle: Text(
                          valorCamion(camion, ['modelo', 'marca', 'descripcion']),
                        ),
                        trailing: Text('#${index + 1}'),
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}