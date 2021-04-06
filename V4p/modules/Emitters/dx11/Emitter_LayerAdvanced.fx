#include <packs\dx11.particles\nodes\modules\Core\fxh\Core.fxh>

struct Particle {
	#if defined(COMPOSITESTRUCT)
  		COMPOSITESTRUCT
 	#else
		float3 position;
		float3 velocity;
		float3 force;
		float lifespan;
		float age;
		float4 color;
		float verletLength;
		float mass;
		float3 scale;
	#endif
};

RWStructuredBuffer<Particle> ParticleBuffer : PARTICLEBUFFER;
RWStructuredBuffer<uint> EmitterCounterBuffer : EMITTERCOUNTERBUFFER;
RWStructuredBuffer<uint> AlivePointerBuffer : ALIVEPOINTERBUFFER;
RWStructuredBuffer<uint> AliveCounterBuffer : ALIVECOUNTERBUFFER;

StructuredBuffer<float3> VelocityBuffer <string uiname="Velocity Buffer";>;
StructuredBuffer<float3> ForceBuffer <string uiname="Force Buffer";>;
//StructuredBuffer<float> LifespanBuffer <string uiname="Lifespan Buffer";>;

Texture2D texRGB <string uiname="RGB";>;
Texture2D texPositionWorld <string uiname="PositionWorld";>;

Texture2D texLifespan <string uiname="Lifespan Texture";>;
Texture2D texVerletLength <string uiname="VerletLength Texture";>;
Texture2D texMass <string uiname="Mass Texture";>;
Texture2D texScale <string uiname="Scale Texture";>;

Texture2D texZDisplace <string uiname="ZDisplace Texture";>;

cbuffer cbuf
{
	uint EmitCount = 0;
	uint EmitterSize = 0;
	float4x4 tW : WORLD;
	float2 Resolution;
	float3 scale <String uiname="Default Scale";> = { 1.0f,1.0f,1.0f };
	float alphaThreshold=0;
	float2 lifespanMinMax;
	float2 verletLengthMinMax;
	float2 massMinMax;
	float2 scaleMinMax;
	bool ForceEmission = false;
}

SamplerState sPoint : IMMUTABLE
{
    Filter = MIN_MAG_MIP_POINT;
    AddressU = Border;
    AddressV = Border;
};

SamplerState sLinear : IMMUTABLE
{
    Filter = MIN_MAG_MIP_LINEAR;
    AddressU = Border;
    AddressV = Border;
};

struct csin
{
	uint3 DTID : SV_DispatchThreadID;
	uint3 GTID : SV_GroupThreadID;
	uint3 GID : SV_GroupID;
};

[numthreads(XTHREADS, YTHREADS, ZTHREADS)]
void CS_Emit(csin input)
{
	if(input.DTID.x >= EmitterSize) return;
	uint particleIndex = EMITTEROFFSET + input.DTID.x;
	
	if( ParticleBuffer[particleIndex].lifespan >= 0) return;
	
	// get XY pixel id 
	uint resX = Resolution.x;
	uint2 texId = int2(input.DTID.x % resX ,input.DTID.x / resX);
	
	uint w,h, dummy;
	texPositionWorld.GetDimensions(0,w,h,dummy);
	
	// calculate sampling coordinates
	float2 texUv = texId * float2(w / Resolution.x , h / Resolution.y) / float2(w,h);
	
	float halfPixel = (1.0f / Resolution.x) * 0.5f;
	texUv += halfPixel;
	

	float4 color = texRGB.SampleLevel(sPoint,texUv,0);
	
	if ( color.a > alphaThreshold || ForceEmission){
		
		
	float4 position = texPositionWorld.SampleLevel(sPoint,texUv,0);
	
	float lifespan = texLifespan.SampleLevel(sPoint,texUv,0).r;
	float verletLength = texVerletLength.SampleLevel(sPoint,texUv,0).r;
	float mass = texMass.SampleLevel(sPoint,texUv,0).r;
	float3 scale = texScale.SampleLevel(sPoint,texUv,0).rgb;
	
	float zDisplace = texZDisplace.SampleLevel(sPoint,texUv,0).r;
		
		
		// INCREMENT EmitterCounter
		uint emitterCounter = EmitterCounterBuffer.IncrementCounter(); 
		if (emitterCounter >= EmitCount )return; // safeguard 
		
		// INIT NEW PARTICLE
		uint size, stride;
		Particle p = (Particle) 0;
	
		// SET POSITION
		p.position = position.xyz - float3(0,0,zDisplace);
		
		// SET COLOR
		p.color = color;
		
		// SET VELOCITY
		VelocityBuffer.GetDimensions(size,stride);
		p.velocity = VelocityBuffer[emitterCounter % size];
		
		// SET force
		ForceBuffer.GetDimensions(size,stride);
		p.force = ForceBuffer[emitterCounter % size];

		// SET LIFESPAN
//		LifespanBuffer.GetDimensions(size,stride);
//		p.lifespan = LifespanBuffer[emitterCounter % size];
		p.lifespan = lerp(lifespanMinMax.x,lifespanMinMax.y,lifespan);
		p.verletLength = lerp(verletLengthMinMax.x,verletLengthMinMax.y,verletLength);
		p.mass = lerp(massMinMax.x,massMinMax.y,mass);
		p.scale = lerp(scaleMinMax.x,scaleMinMax.y,scale);
//		p.radius = 1;
		
		// SET DEFAULT SCALE (IF SCALE ATTRIBUTE IS PRESENT)
		#if defined(KNOW_SCALE)
            p.scale = scale;
    	#endif
        
		// ADD PARTICLE TO PARTICLEBUFFER
		ParticleBuffer[particleIndex] = p;
				
		// UPDATE ALIVEPOINTERBUFFER
		uint aliveIndex = AliveCounterBuffer[0] + AliveCounterBuffer.IncrementCounter();
		AlivePointerBuffer[aliveIndex] = particleIndex;
	}
	
}

technique11 EmitParticles
{
	pass P0
	{
		SetComputeShader( CompileShader( cs_5_0, CS_Emit() ) );
	}
}