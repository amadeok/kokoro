
from kokoro import KPipeline
import soundfile as sf
import torch
pipeline = KPipeline(lang_code='e')
#more languages at kokoro.js\src\voices.js
text = '''
[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.
'''
text = '''
El español es un idioma romance originado en la región de Castilla, España. También es conocido como castellano y es hablado por millones de personas en todo el mundo. Es el segundo idioma materno más hablado a nivel mundial y el cuarto en el cómputo general de hablantes. Además, es uno de los seis idiomas oficiales de las Naciones Unidas. 
'''
print(len(text))
generator = pipeline(text, voice='em_alex')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps, len(ps))

    sf.write(f'{i}.wav', audio, 24000)
    
    
    