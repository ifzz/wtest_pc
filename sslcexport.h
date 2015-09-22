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
//����Ľṹ����һ�ֽڶ���
struct	CommPackInfo
{
	DWORD			crc32;				// ��ͷУ��(У�������ͺ��������)
	// �����濪ʼ����У��ͣ�һֱ���������������
	unsigned char	Compressed;			// ѹ�����߼��ܣ����������(0 : û��ѹ����1��zlib��2��cѹ��)
	unsigned char	packtype;			// ����Э�����ͣ������Ҫ������࣬���д���
	DWORD			cookie;				// �û��ϲ��Լ�Я������Ϣ
	DWORD			synID;				// ͬ��ID������ʹ�õ��첽��Ϣ
	DWORD			rawLen;				// ԭʼû��ѹ���ĳ���
	DWORD			packlen;			// ����,��������ͷ�Լ�;�ŵ���ǰ�����Լ�������ϵͳ
	char			packdata[0];		// ���������(ʵ��Ҫ���������)
};
#pragma pack(pop,1)

extern "C" 
{
	/*��ʼ������,����һ���������, ����0Ϊʧ��,�����ɹ�,�������ֵ���Ժ�ÿ��������һ��������Ҫ�õ�,DZH_DATA_Init()���������º�������֮ǰ���ȵ���
	id��ʾȯ�̱�ʶ,����"����֤ȯ",����ʵ���������
	outbuffer,outlen��ʾ��ʼ�����ص�����,���outlen���Ȳ�Ϊ0,Ӧ��������send()���ͻط�����
	������ص�outbuffer��Ϊ��,����Ӧ�õ���DZH_DATA_FreeBuf()�ͷ�
	*/
	OPENDLL_API  int  DZH_DATA_Init(const char * id,unsigned char* &outbuffer, unsigned int& outlen);
	//������º������ó���,�˺������س��������
	OPENDLL_API  const char * DZH_DATA_GetLastErr(int h);
	/*�������������ֵ�İ�,�����յ����κΰ�,��Ӧ�ý��������������
	����DZH_DATA_ProcessServerData����պ�һ�������İ�,��CommPackInfo��packlen��ָʾ�ĳ��ȸո��յ�,���಻��
	
	  ����ֵ˵��
	  ����0,��ʾoutbuffer�������Ѿ����ܽ�ѹ�ɿͻ�����,���������Ƿ����ڲ�ί��Э�������,
	  ����1,��ʾoutbuffer��������Ҫ�����ͻط����,����������Ѿ������,ֱ�ӵ�send()���;Ϳ�����
	  ����2,��ʾoutbuffer��������ί���ֵ�����,�ͻ�Ӧ�����ڴ��б����Լ���Ҫ�õ����ֵ�,����2��ʾ�ͷ���˵İ�ȫ���������
	  ����ֵС��0����ʾ�Ƿ���У�鲻ͨ������Ϣ,������DZH_DATA_GetLastErr()��ѯ����ԭ��
	  ����˵��
	  h,�������,��DZH_DATA_Init()����
	  info,���������ص�һ���������ݰ�
	  outbuffer,���ص�����,������ֵΪ0��1ʱ,Ӧ�õ���DZH_DATA_FreeBuf()�ͷ��²���������ڴ�
	  outlen,���ص����ݳ���
	*/
	OPENDLL_API  int DZH_DATA_ProcessServerData(int h,CommPackInfo *info,unsigned char* &outbuffer, unsigned int& outlen);
	//�ͷ��²���������ڴ�
	OPENDLL_API void DZH_DATA_FreeBuf(int h,unsigned char * buf);
	/*
	��װ�ͻ���Ҫ���͵İ�(��Ӧ��Э��C��������)
	����˵��
	h,�������,��DZH_DATA_Init()����
	cookie,�ͻ�����������
	synID,ͬ��id,����˻�Ӧ��ԭ������
	data,Ҫ���͵��ڲ�ί��Э������
	datalen,Ҫ���͵��ڲ�ί��Э�����ݳ�
	outbuffer,�²����������,����ֱ����send()����,����ɹ�ʱ,Ӧ�õ���DZH_DATA_Free()�ͷ��²���������ڴ�
	outlen,�²���������ݵĳ���
	����ֵ˵��
	����-1,���ʧ��,������DZH_DATA_GetLastErr()��ѯ����ԭ��
	����ֵ:����ɹ�
	*/
	OPENDLL_API  int DZH_DATA_CreatePackage(int h,DWORD cookie,DWORD synID,unsigned char *data,unsigned int datalen,unsigned char* &outbuffer, unsigned int& outlen);
	

	/*
	�ͷŻ������
	���������������ϵ�ĳ��������������û������˳���Ӧ�õ���DZH_DATA_Uninit()�ͷ�ռ�õ���Դ,һ��DZH_DATA_Uninit()�����Ժ󻷾������ɲ�����,�����õ�
	�����������ĺ����������ٵ���
	*/
	OPENDLL_API void DZH_DATA_Uninit(int h);
}

#endif // !defined(AFX_SSLCEXPORT_H__93305D1A_E193_45DB_A0A3_05EDF5DB70B1__INCLUDED_)
