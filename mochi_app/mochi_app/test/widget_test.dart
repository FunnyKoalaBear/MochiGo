import 'package:flutter/material.dart';
import 'dart:math' as math; // Used for simple sakura drawing math

// --- THE LAUNCHER ---
void main() {
  runApp(const MochiStudyApp());
}

class MochiStudyApp extends StatelessWidget {
  const MochiStudyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mochi Study',
      debugShowCheckedModeBanner: false, 
      theme: ThemeData(
        // The deeper pastel pink background for better Mochi contrast
        scaffoldBackgroundColor: const Color(0xFFFFE0E6),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}

// --- THE LOGIN SCREEN (DUAL-TRACKING WRAPPER) ---
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final GlobalKey _mochiKey = GlobalKey();
  Offset _lookDirection = Offset.zero;

  // Handles both mouse hover (web/desktop) and finger move (mobile)
  void _calculateLookDirection(Offset eventPosition) {
    final RenderBox? renderBox = _mochiKey.currentContext?.findRenderObject() as RenderBox?;
    if (renderBox == null) return;

    final mochiPosition = renderBox.localToGlobal(Offset.zero);
    final mochiCenter = mochiPosition + Offset(renderBox.size.width / 2, renderBox.size.height / 2);

    final touchPosition = eventPosition;
    final rawOffset = touchPosition - mochiCenter;

    final double maxDistance = 300; 
    double normalizedX = (rawOffset.dx / maxDistance).clamp(-1.0, 1.0);
    double normalizedY = (rawOffset.dy / maxDistance).clamp(-1.0, 1.0);

    setState(() {
      _lookDirection = Offset(normalizedX, normalizedY);
    });
  }

  @override
  Widget build(BuildContext context) {
    // --- 1. DUAL-TRACKING ARCHITECTURE ---
    
    // MouseRegion handles desktop/web 'hover' (cursor movement without clicks)
    return MouseRegion(
      onHover: (event) => _calculateLookDirection(event.position),
      // Standard Listener handles touch screen dragging/moving
      child: Listener(
        onPointerMove: (event) => _calculateLookDirection(event.position),
        onPointerDown: (event) => _calculateLookDirection(event.position), // Taps still work too!
        child: Scaffold(
          backgroundColor: const Color(0xFFFFE0E6),
          body: SafeArea(
            child: Center(
              child: SingleChildScrollView(
                physics: const ClampingScrollPhysics(), 
                padding: const EdgeInsets.symmetric(horizontal: 32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SizedBox(height: 20),
                    
                    // The Lamp-shape Mochi (key attached for tracking)
                    SquishyMochi(
                      key: _mochiKey,
                      lookOffset: _lookDirection,
                    ),
                    
                    const SizedBox(height: 32),
                    const Text(
                      "Welcome back!",
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFFF8C94),
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      "Mochi is ready to study with you.",
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.black54,
                      ),
                    ),
                    const SizedBox(height: 40),
                    _buildSoftTextField(
                      hintText: "Email",
                      icon: Icons.email_rounded,
                    ),
                    const SizedBox(height: 16),
                    _buildSoftTextField(
                      hintText: "Password",
                      icon: Icons.lock_rounded,
                      isObscure: true,
                    ),
                    const SizedBox(height: 40),
                    SizedBox(
                      width: double.infinity,
                      height: 55,
                      child: ElevatedButton(
                        onPressed: () {
                          // ignore: avoid_print
                          print("Logging in...");
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFFF8C94),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(30),
                          ),
                        ),
                        child: const Text(
                          "Let's Study!",
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSoftTextField({required String hintText, required IconData icon, bool isObscure = false}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.pink.withValues(alpha: 0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: TextField(
        obscureText: isObscure,
        decoration: InputDecoration(
          border: InputBorder.none,
          prefixIcon: Icon(icon, color: const Color(0xFFFF8C94)),
          hintText: hintText,
          hintStyle: const TextStyle(color: Colors.black26),
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        ),
      ),
    );
  }
}

// --- THE MOCHI LAMP DESIGN (updated with Sakura) ---
class SquishyMochi extends StatefulWidget {
  final Offset lookOffset;

  const SquishyMochi({super.key, required this.lookOffset});

  @override
  State<SquishyMochi> createState() => _SquishyMochiState();
}

class _SquishyMochiState extends State<SquishyMochi> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500), 
      vsync: this,
    )..repeat(reverse: true); 

    _animation = Tween<double>(begin: 1.0, end: 0.90).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.scale(
          scaleY: _animation.value, 
          scaleX: 1.0 + (1.0 - _animation.value) * 0.15, 
          alignment: Alignment.bottomCenter, 
          child: child,
        );
      },
      child: Container(
        width: 220,
        height: 140,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(100),
            topRight: Radius.circular(100),
            bottomLeft: Radius.circular(20), 
            bottomRight: Radius.circular(20),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            // --- THE GLOWING INNER SCREEN ---
            Transform.translate(
              // The central face area follows the cursor
              offset: Offset(widget.lookOffset.dx * 8, widget.lookOffset.dy * 4),
              child: Container(
                width: 110,
                height: 60,
                decoration: BoxDecoration(
                  color: const Color(0xFFFFFDF5), 
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFFFF0C2).withValues(alpha: 0.8), 
                      blurRadius: 15,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: Center(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _buildPinchEye('>'),
                      const SizedBox(width: 15), 
                      _buildPinchEye('<'),
                    ],
                  ),
                ),
              ),
            ),
            
            // --- 2. THE SAKURA ACCESSORY ---
            // Positioned on the upper-right head area
            const Positioned(
              top: 15,
              right: 35,
              child: MochiSakuraflower(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPinchEye(String character) {
    return Text(
      character,
      style: const TextStyle(
        fontSize: 38,
        fontWeight: FontWeight.w600,
        color: Color(0xFF333333), 
        height: 1.0, 
      ),
    );
  }
}

// --- PURE CODE SAKURA FLOWER WIDGET ---
class MochiSakuraflower extends StatelessWidget {
  const MochiSakuraflower({super.key});

  @override
  Widget build(BuildContext context) {
    // A simplified 5-petal cherry blossom using nested containers
    return Stack(
      alignment: Alignment.center,
      children: [
        // The petals ring
        for (int i = 0; i < 5; i++)
          Transform.rotate(
            angle: (i * (360 / 5)) * (math.pi / 180), // Rotate 5 petals around center
            child: Transform.translate(
              offset: const Offset(0, -6), // Shift petals outward from center
              child: Container(
                width: 12,
                height: 16,
                decoration: BoxDecoration(
                  color: const Color(0xFFFFBCC9), // Sweet sakura pink
                  borderRadius: BorderRadius.circular(6), // Petal shape
                ),
              ),
            ),
          ),
        // Central small yellow part
        Container(
          width: 8,
          height: 8,
          decoration: const BoxDecoration(
            color: Color(0xFFFFF49C), // Sakura center
            shape: BoxShape.circle,
          ),
        ),
      ],
    );
  }
}