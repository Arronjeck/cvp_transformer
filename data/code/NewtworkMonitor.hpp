#pragma once
#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>
#include <functional>
#include <condition_variable>
#include <set>

#include <WinInet.h>
#pragma comment(lib,"Wininet.lib")

namespace NetworkMNO
{

typedef void(*fnNetMoniterCallback)(BOOL netstatus);

class NetworkMoniter
{
public:
	static NetworkMoniter* GetInstance()
	{
		static NetworkMoniter n;
		return &n;
	}

	~NetworkMoniter()
	{
		stop(nullptr);
	}

	bool update_rate(int millisecond)
	{
		_rate = millisecond;
	}

	bool start(fnNetMoniterCallback cbk)
	{
		std::unique_lock<std::mutex> lck(_mtx);

		auto retpair = _moniters.insert(cbk);
		if (!retpair.second)
			return true;

		if (_stop)
		{
			_stop = false;

			auto work = std::bind(&NetworkMoniter::work_thread, this);
			_t = std::thread(work);
		}
		return true;
	}

	bool stop(fnNetMoniterCallback cbk)
	{
		bool wait = false;

		{
			std::unique_lock<std::mutex> lck(_mtx);

			if (cbk) {
				for (const auto& it : _moniters) {
					if (it == cbk) {
						_moniters.erase(it);
						break;
					}
				}
			}
			else {
				_moniters.clear();
			}

			if (_moniters.size() == 0 && !_stop) {
				wait = true;
				_stop = true;
				_cv.notify_one();
			}
		}

		if (_stop && wait && _t.joinable()) {
			_t.join();
		}

		return true;
	}



public:

	void work_thread()
	{	
		std::unique_lock<std::mutex> lck(_mtx);
		
		while (true)
		{
			bool rc = _cv.wait_for(lck, std::chrono::milliseconds(_rate), [&]()->bool {
				return _stop;
			});
		  
			if (!rc) {
				DWORD flagsConnected;
				bool rc = ::InternetGetConnectedState(&flagsConnected, 0) ? true : false;

				for (auto v : _moniters)
					v(rc);  
			}
			else
			{
				break;
			}
		}

		std::cout << "Work thread exit!!! threadId = " << std::this_thread::get_id() << std::endl;
	}

private:
	bool _stop = true;
	int _rate = 3 * 1000;

	using MONITERS = std::set<fnNetMoniterCallback>;
	MONITERS _moniters;

	std::thread _t;
	std::mutex  _mtx;
	std::condition_variable _cv;
};

inline void SetCallbackRate(int millisecond)
{
	NetworkMoniter::GetInstance()->update_rate(millisecond);
}

inline bool StartNetworkMoniter(fnNetMoniterCallback callback)
{
	if (!callback)
		return false;

	return NetworkMoniter::GetInstance()->start(callback);
}

inline bool StopNetworkMoniter(fnNetMoniterCallback callback = nullptr)
{
	return NetworkMoniter::GetInstance()->stop(callback);
}

};