/* The following includes are mandatory! */
#include <packs\dx11.particles\nodes\modules\Core\fxh\Core.fxh>
#include <packs\dx11.particles\nodes\modules\Core\fxh\IndexFunctions_Particles.fxh>
#include <packs\dx11.particles\nodes\modules\Core\fxh\IndexFunctions_DynBuffer.fxh>
/* Have a look at the packs\dx11.particles\nodes\modules\Core\ directory for more helper functions */

/* Like described in the template patch, the attribute(s) for the particlesystem is registered here*/ 
struct Particle {
	#if defined(COMPOSITESTRUCT)
  		COMPOSITESTRUCT
 	#else
		float age;
		float lifespan;
		float3 force;
		float3 velocity;
	#endif
};

/* The ParticleBuffer and the UseSelectionIndex variable are mandatory*/
RWStructuredBuffer<Particle> ParticleBuffer : PARTICLEBUFFER;

struct csin
{
	uint3 DTID : SV_DispatchThreadID;
	uint3 GTID : SV_GroupThreadID;
	uint3 GID : SV_GroupID;
};

[numthreads(XTHREADS, YTHREADS, ZTHREADS)]
void CSSet(csin input)
{
	/* Always use these lines to get the particleIndex! */
	uint particleIndex = GetParticleIndex( input.DTID.x );
	if (particleIndex == -1 ) return;
	
	/* There are different ways to access the data in your DynamicBuffer:
		a) Apply modifier to ALL particles
		b) Apply modifier to SELECTED particles (wrt. selectionIndex)
	   The following code shows, how you should access your bufferdata. You should
	   always do it like that:
	*/
	// 1) Get size of the buffer
	uint size, stride;
	// 2) Get the index into your buffer
	uint bufferIndex = GetDynamicBufferIndex( particleIndex, input.DTID.x , size);
	
	if (ParticleBuffer[particleIndex].age > ParticleBuffer[particleIndex].lifespan + 10){
		
	ParticleBuffer[particleIndex].force = 0;
	ParticleBuffer[particleIndex].velocity = 0;
		
	}
	
	// That's it! Have a look into existing modifiers for more complex examples (f.e. SelfRepulsion)
}

technique11 Set { pass P0{SetComputeShader( CompileShader( cs_5_0, CSSet() ) );} }