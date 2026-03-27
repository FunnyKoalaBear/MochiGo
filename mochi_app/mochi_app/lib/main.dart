import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:math' as math;
import 'package:audioplayers/audioplayers.dart'; 

// --- THE LAUNCHER ---
void main() {
  runApp(const MochiVoiceApp());
}

class MochiVoiceApp extends StatelessWidget {
  const MochiVoiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mochi Voice',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: const Color(0xFFFFE0E6),
        useMaterial3: true,
      ),
      home: const VoiceScreen(),
    );
  }
}

// --- THE VOICE UI SCREEN ---
class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});

  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  bool _isListening = false;
  Timer? _silenceTimer;
  
  final AudioPlayer _audioPlayer = AudioPlayer();

  @override
  void dispose() {
    _silenceTimer?.cancel();
    _audioPlayer.dispose(); 
    super.dispose();
  }

  void _toggleListening() {
    if (_isListening) {
      _stopListening();
    } else {
      _startListening();
    }
  }

  void _startListening() async {
    setState(() {
      _isListening = true;
    });
    
    await _audioPlayer.play(AssetSource('bubble.mp3'));
    // TODO: ADD STT FUNCTION HERE 
    print("Microphone OPEN - Listening to user...");
    _resetSilenceTimer();
  }

  void _stopListening() async {
    _silenceTimer?.cancel(); 
    setState(() {
      _isListening = false;
    });

    print("Microphone CLOSED - Going back to sleep...");
  }

  void _resetSilenceTimer() {
    _silenceTimer?.cancel(); 
    _silenceTimer = Timer(const Duration(seconds: 10), () {
      if (mounted && _isListening) {
        print("10 seconds of silence detected. Auto-stopping!");
        _stopListening();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFE0E6),
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // --- THE INTERACTIVE MOCHI BUTTON ---
              GestureDetector(
                onTap: _toggleListening,
                behavior: HitTestBehavior.translucent, 
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      if (_isListening)
                        BoxShadow(
                          color: Colors.white.withValues(alpha: 0.6),
                          blurRadius: 60,
                          spreadRadius: 20,
                        ),
                    ],
                  ),
                  child: SquishyMochi(isListening: _isListening),
                ),
              ),
              
              const SizedBox(height: 50),
              
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: Text(
                  _isListening ? "Listening..." : "Tap Mochi to wake her up",
                  key: ValueKey<bool>(_isListening),
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: _isListening ? FontWeight.bold : FontWeight.normal,
                    color: _isListening ? const Color(0xFFFF8C94) : Colors.black45,
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
              
              AnimatedOpacity(
                opacity: _isListening ? 1.0 : 0.0,
                duration: const Duration(milliseconds: 200),
                child: const Icon(
                  Icons.mic_rounded,
                  color: Color(0xFFFF8C94),
                  size: 32,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- THE MOCHI DESIGN ---
class SquishyMochi extends StatefulWidget {
  final bool isListening;

  const SquishyMochi({super.key, required this.isListening});

  @override
  State<SquishyMochi> createState() => _SquishyMochiState();
}

class _SquishyMochiState extends State<SquishyMochi> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  
  bool _isBlinking = false;
  Timer? _blinkTimer;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 2500),
      vsync: this,
    )..repeat(reverse: true);

    _animation = Tween<double>(begin: 1.0, end: 0.90).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    _scheduleNextBlink();
  }

// --- BREATHING---
  @override
  void didUpdateWidget(SquishyMochi oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isListening != oldWidget.isListening) {
      if (widget.isListening) {
        _controller.duration = const Duration(milliseconds: 1000);
      } else {
        _controller.duration = const Duration(milliseconds: 2500);
      }
      _controller.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _blinkTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _scheduleNextBlink() {
    final randomDelay = 2000 + math.Random().nextInt(4000); 
    _blinkTimer = Timer(Duration(milliseconds: randomDelay), () {
      if (mounted) {
        setState(() => _isBlinking = true); 
        
        Future.delayed(const Duration(milliseconds: 150), () {
          if (mounted) {
            setState(() => _isBlinking = false);
            _scheduleNextBlink(); 
          }
        });
      }
    });
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
            Container(
              width: 120, 
              height: 60,
              decoration: BoxDecoration(
                color: const Color(0xFFFFFDF5),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: widget.isListening 
                        ? const Color(0xFFFF8C94).withValues(alpha: 0.4) 
                        : const Color(0xFFFFF0C2).withValues(alpha: 0.8), 
                    blurRadius: 15,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      AnimatedEye(isListening: widget.isListening, isBlinking: _isBlinking),
                      const SizedBox(width: 20), 
                      AnimatedEye(isListening: widget.isListening, isBlinking: _isBlinking),
                    ],
                  ),
                  AnimatedOpacity(
                    opacity: widget.isListening ? 1.0 : 0.0,
                    duration: const Duration(milliseconds: 300),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _buildCheek(),
                        const SizedBox(width: 45), 
                        _buildCheek(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // --- THE SAKURA EMOJI ---
            Positioned(
              top: 5,
              right: 18,
              child: Transform.rotate(
                angle: 0.2,
                child: const Text(
                  "🌸",
                  style: TextStyle(fontSize: 32),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCheek() {
    return Container(
      margin: const EdgeInsets.only(top: 25), 
      width: 18,
      height: 8,
      decoration: BoxDecoration(
        color: const Color(0xFFFF8C94).withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(10),
      ),
    );
  }
}

// --- THE EYE WIDGET ---
class AnimatedEye extends StatelessWidget {
  final bool isListening;
  final bool isBlinking;

  const AnimatedEye({
    super.key, 
    required this.isListening, 
    required this.isBlinking,
  });

  @override
  Widget build(BuildContext context) {
    final double eyeWidth = isListening ? 22.0 : 16.0;
    final double eyeHeight = isListening ? (isBlinking ? 4.0 : 22.0) : 4.0;
    final Color eyeColor = isListening ? const Color(0xFF5A4A4A) : const Color(0xFFB0A0A0);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300), 
      curve: Curves.easeOutBack, 
      width: eyeWidth,
      height: eyeHeight,
      decoration: BoxDecoration(
        color: eyeColor,
        borderRadius: BorderRadius.circular(15), 
      ),
      child: Stack(
        children: [
          if (isListening && !isBlinking)
            Positioned(
              top: 3,
              right: 4,
              child: AnimatedOpacity(
                duration: const Duration(milliseconds: 200),
                opacity: isListening ? 1.0 : 0.0,
                child: Container(
                  width: 6,
                  height: 6,
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}