"""Small original synthesized interface cues, no external audio dependency."""
from pathlib import Path
import wave,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'assets/sounds';folder.mkdir(exist_ok=True);rate=44100
def tone(freq,duration,brightness=.1):
    t=np.arange(int(duration*rate))/rate
    envelope=(1-np.exp(-t*1400))*np.exp(-t*max(14,5/duration))
    return envelope*(np.sin(t*freq*2*np.pi)+brightness*np.sin(t*freq*4*np.pi))
def notes(values,duration=.07):return np.concatenate([tone(f,duration) for f in values])
rng=np.random.default_rng(1700)
click=tone(1550,.028,.2);click+=rng.normal(0,.16,len(click))*np.exp(-np.arange(len(click))/100)
sounds={'click':click,'select':notes([660,880],.042),'confirm':notes([660,830,990],.065),'error':notes([330,247],.08),'open':notes([440,554],.065)}
report={}
for name,data in sounds.items():
    data=data/max(1,np.max(np.abs(data)))*.55;pcm=(data*32767).astype('<i2')
    with wave.open(str(folder/(name+'.wav')),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm.tobytes())
    report[name]={'seconds':len(data)/rate,'peak':float(np.max(np.abs(data))),'samples':len(data)}
(ROOT/'data/sounds_017_report.json').write_text(json.dumps(report,indent=2));print('SOUNDS_017_COMPLETE',len(sounds))
