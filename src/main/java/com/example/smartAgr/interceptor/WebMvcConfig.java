package com.example.smartAgr.interceptor;

import com.example.smartAgr.interceptor.JwtAdminInterceptor;
import com.example.smartAgr.interceptor.JwtUserInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Autowired
    private JwtAdminInterceptor jwtAdminInterceptor;
    @Autowired
    private JwtUserInterceptor jwtUserInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtAdminInterceptor)
                .addPathPatterns("/admin/**")
                .excludePathPatterns("/admin/login");

        registry.addInterceptor(jwtUserInterceptor)
                .addPathPatterns("/user/**")
                .excludePathPatterns("/user/login");
    }

    // 跨域配置
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("http://123.56.228.32:8080") // 生产环境建议具体域名
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("Origin", "Content-Type", "Accept", "authentication", "Authorization", "X-Requested-With")
                .allowCredentials(true);
    }
}
