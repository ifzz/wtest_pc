// sslcexport.h: interface for the sslcexport class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_SSLCEXPORT_H__93305D1A_E193_45DB_A0A3_05EDF5DB70B1__INCLUDED_)
#define AFX_SSLCEXPORT_H__93305D1A_E193_45DB_A0A3_05EDF5DB70B1__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifdef OPENDLL_EXPORTS
#define OPENDLL_API __declspec(dllexport)
#else
#define OPENDLL_API __declspec(dllimport)
#endif

#pragma pack(push,1)
//下面的结构都是一字节对齐
struct	CommPackInfo
{
	DWORD			crc32;				// 包头校验(校验整个和后面的数据)
	// 从下面开始计算校验和，一直到后面的数据内容
	unsigned char	Compressed;			// 压缩或者加密，混合最多情况(0 : 没有压缩；1：zlib；2：c压缩)
	unsigned char	packtype;			// 常见协议类型，如果需要具体分类，自行处理
	DWORD			cookie;				// 用户上层自己携带的信息
	DWORD			synID;				// 同步ID，保留使用的异步信息
	DWORD			rawLen;				// 原始没有压缩的长度
	DWORD			packlen;			// 包长,不包括包头自己;放到最前，可以兼容其他系统
	char			packdata[0];		// 后面的数据(实际要传输的数据)
};
#pragma pack(pop,1)

extern "C" 
{
	/*初始化环境,返回一个环境句柄, 返回0为失败,其它成功,这个返回值在以后每个函数第一个参数都要用到,DZH_DATA_Init()必须在以下函数调用之前最先调用
	id表示券商标识,比如"招商证券",根据实际情况传入
	outbuffer,outlen表示初始化返回的数据,如果outlen长度不为0,应该马上用send()发送回服务器
	如果返回的outbuffer不为空,用完应该调用DZH_DATA_FreeBuf()释放
	*/
	OPENDLL_API  int  DZH_DATA_Init(const char * id,unsigned char* &outbuffer, unsigned int& outlen);
	//如果以下函数调用出错,此函数返回出错的描述
	OPENDLL_API  const char * DZH_DATA_GetLastErr(int h);
	/*处理服务器返回值的包,服务收到的任何包,都应该交给这个函数处理
	传给DZH_DATA_ProcessServerData必须刚好一个完整的包,即CommPackInfo中packlen所指示的长度刚刚收到,不多不少
	
	  返回值说明
	  返回0,表示outbuffer中数据已经解密解压由客户处理,这里数据是符合内部委托协议的数据,
	  返回1,表示outbuffer中数据需要立即送回服务端,这个数据是已经封包的,直接调send()发送就可以了
	  返回2,表示outbuffer中数据是委托字典数据,客户应该在内存中保存自己所要用到的字典,返回2表示和服务端的安全交互完成了
	  返回值小于0，表示非法或校验不通过等信息,可以由DZH_DATA_GetLastErr()查询出错原因
	  参数说明
	  h,环境句柄,由DZH_DATA_Init()返回
	  info,服务器返回的一个完整数据包
	  outbuffer,返回的数据,当返回值为0或1时,应该调用DZH_DATA_FreeBuf()释放下层所分配的内存
	  outlen,返回的数据长度
	*/
	OPENDLL_API  int DZH_DATA_ProcessServerData(int h,CommPackInfo *info,unsigned char* &outbuffer, unsigned int& outlen);
	//释放下层所分配的内存
	OPENDLL_API void DZH_DATA_FreeBuf(int h,unsigned char * buf);
	/*
	封装客户端要发送的包(对应于协议C发送数据)
	参数说明
	h,环境句柄,由DZH_DATA_Init()返回
	cookie,客户端其它数据
	synID,同步id,服务端回应包原样返回
	data,要发送的内部委托协议数据
	datalen,要发送的内部委托协议数据长
	outbuffer,下层封包后的数据,可以直接用send()发送,封包成功时,应该调用DZH_DATA_Free()释放下层所分配的内存
	outlen,下层封包后的数据的长度
	返回值说明
	返回-1,封包失败,可以由DZH_DATA_GetLastErr()查询出错原因
	其他值:封包成功
	*/
	OPENDLL_API  int DZH_DATA_CreatePackage(int h,DWORD cookie,DWORD synID,unsigned char *data,unsigned int datalen,unsigned char* &outbuffer, unsigned int& outlen);
	

	/*
	释放环境句柄
	当网络出错或者以上的某个函数出错或者用户主动退出都应该调用DZH_DATA_Uninit()释放占用的资源,一旦DZH_DATA_Uninit()调用以后环境句柄变成不可用,所有用到
	这个环境句柄的函数都不能再调用
	*/
	OPENDLL_API void DZH_DATA_Uninit(int h);
}

#endif // !defined(AFX_SSLCEXPORT_H__93305D1A_E193_45DB_A0A3_05EDF5DB70B1__INCLUDED_)
